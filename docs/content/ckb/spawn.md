# CKB/Spawn: a new cross script calling method

Hey everyone! Today, I'd like to introduce some exciting new features in ckb script development. One of these features is spawn, which was added as part of the ckb meepo hard fork. The meepo hard fork introduced several interesting changes, and spawn is one of the key additions.

In ckb script, spawn refers to a concept and a set of syscalls used for creating new processes. Unlike [exec syscall](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0034-vm-syscalls-2/0034-vm-syscalls-2.md#exec), introduced during the mirana hard fork, spawn provides a more direct way to enable cross-script calls, making the process simpler while offering greater control and optimization.

## Background

In 2021, during the mirana hard fork, we introduced the exec syscall in the ckb-vm. Exec allows loading and executing a new script within the current execution space. While this feature is powerful, it can sometimes be inefficient, particularly when the current execution space needs to be preserved. Specifically, when using exec, all state information about the current script is discarded. As illustrated in the figure below, when script a calls script b using exec, the context of script a is lost.

```text
      +----------+   Exec   +----------+
----->+ Script A +--------->+ Script B +---->
      +----------+          +----------+
```

We hope to find a way to preserve the context of script a. Ideally, when script b is executed, script a would be able to retrieve the execution result of script b and then continue its own execution. The process should look like what is shown in the figure below:

```text
      +----------+
----->+ Script A +--------------+----------->
      +-----+----+              ^
            |                   |
            | Spawn             | Exit
            v                   |
      +----------+              |
      | Script B +--------------+
      +----------+
```

Yes, this is what spawn is supposed to do.

## Development of spawn in ckb-vm

The spawn family of syscalls in the ckb-vm is inspired by the linux standard, providing developers with an efficient way to create processes. As a result, it uses familiar terminology like process, pipe, and file descriptor. We've invested significant effort to make this new technology as user-friendly as possible, allowing you to develop multi-process applications as easily as you would on a local system.

```text
                    +--------------------+          .--.
                    | Hi, CKB, This is   |         .-    \
                    | 0. Process         |        /_      \
           +-----+  | 1. Pipe            |       (o        ) +-------+
           | CKB |  | 2. File Descriptor |     _/          | | Linux |
           +-----+  +--------------------+    (c       .-. | +-------+
             ___                  ;;          /      .'   \
          .''   ``.               ;;         O)     |      \
        _/ .-. .-. \_     () ()  / _          `.__  \       \
       (o|( O   O )|o)   ()(O)() |/ )           /    \       \
        .'         `.      ()\  _|_            /      \       \
       /    (c c)    \        \(_  \          /        \       \
       |             |        (__)  `.______ ( ._/      \       )
       \     (o)     /        (___)`._      .'           )     /
        `.         .'         (__)  ______ /            /     /
          `-.___.-'            /|\         |           /     /
          ___)(___            /  \         \          /     /
       .-'        `-.                       `.      .'     /
      / .-.      .-. \                        `-  /.'     /
     / /  ( .  . )  \ \                         / \)| | | |
    / /    \    /    \ \                       /     \_\_\_)
    \ \     )  (     / /                     (    /
     \ \   ( __ )   / /                        \   \ \  \
    /   )  //  \\  (   \                        \   \ \  \
(\ / / /\) \\  // (/\ \ \ /)                     )   \ \  \
 -'-'-'  .'  )(  `.  `-`-`-                     .'   |.'   |
       .'_ .'  `. _`.                      _.--'     (     (
     oOO(_)      (_)OOo                   (__.--._____)_____)
```

To avoid any confusion between processes in the ckb-vm and those in an operating system, let me clarify what "processes" in the ckb-vm refer to. In the ckb-vm, every running script is considered a process. A process is essentially an entity with its own independent execution space. At the operating system level, ckb-vm is still a single-process, single-threaded program.

## Overview of the spawn family of syscalls

In the ckb-vm, spawn is primarily implemented through the spawn() and spawn_cell() functions. These two functions offer nearly the same functionality, with the key difference being that spawn_cell() locates the script using the code_hash and hash_type, while spawn() requires the developer to provide an absolute index and source.

Their function signatures are as follows:

```rs
pub fn spawn(
    index: usize,
    source: Source,
    place: usize,
    bounds: usize,
    spgs: &mut SpawnArgs,
) -> Result<u64, SysError>;
```

```rs
pub fn spawn_cell(
    code_hash: &[u8],
    hash_type: ScriptHashType,
    argv: &[&CStr],
    inherited_fds: &[u64],
) -> Result<u64, SysError>;
```

At a low level, spawn_cell() is simply a wrapper around spawn(). Therefore, I will primarily focus on the spawn() function. The parameters for this function are explained as follows:

- index: an index value denoting the index of entries to read.
- source: a flag denoting the source of cells or witnesses to locate, possible values include:
    - 1: input cells.
    - 0x0100000000000001: input cells with the same running script as current script
    - 2: output cells.
    - 0x0100000000000002: output cells with the same running script as current script
    - 3: dep cells.
- place: A value of 0 or 1:
    - 0: read from cell data
    - 1: read from witness
- bounds: high 32 bits means offset, low 32 bits means length. if length equals to zero, it read to end instead of reading 0 bytes.
- spawn_args: pass data during process creation or save return data. It is a structure with four members:
    - argc: argc contains the number of arguments passed to the program
    - argv: argv is a one-dimensional array of strings
    - process_id: a pointer used to save the process_id of the child process
    - inherited_fds: an array representing the file descriptors passed to the child process. It must end with zero, for example, when you want to pass fd1 and fd2, you need to construct an array [fd1, fd2, 0].

The arguments used here - index, source, bounds, place, argc, and argv - it's exactly the same as exec().

Like linux, ckb-vm uses pipes and file descriptors to pass data between processes.

```rs
pub fn pipe() -> Result<(u64, u64), SysError>;
```

The pipe() creates a pipe, a unidirectional data channel that can be used for interprocess communication. The tuple of returns is used to return two file descriptors referring to the ends of the pipe. The first element refers to the read end of the pipe. The second element refers to the write end of the pipe. Data written to the write end of the pipe is buffered by the ckb-vm until it is read from the read end of the pipe.

```text
                __------__
              /~          ~\     +--------------------------------------------+
             |    //^\\//^\|     | Pipe create a unidirectional data channel, |
           /~~\  ||  o| |o|:~\   | data can be written to or read from a pipe |
          | |6   ||___|_|_||:|   +--------------------------------------------+
           \__.  /      o  \/'
            |   (       O   )
   /~~~~\    `\  \         /
  | |~~\ |     )  ~------~`\
 /' |  | |   /     ____ /~~~)\
(_/'   | | |     /'    |    ( |
       | | |     \    /   __)/ \
       \  \ \      \/    /' \   `\
         \  \|\        /   | |\___|
           \ |  \____/     | |
           /^~>  \        _/ <
          |  |         \       \
          |  | \        \        \
          -^-\  \       |        )
               `\_______/^\______/
```

```rs
pub fn read(fd: u64, buffer: &mut [u8]) -> Result<usize, SysError>;
```

The read() function attempts to read up to the number of bytes specified by length from the file descriptor fd into the buffer, returning the actual number of bytes read.


```rs
pub fn write(fd: u64, buffer: &[u8]) -> Result<usize, SysError>;
```

The counterpart to the read() function is write(). This syscall writes data to a pipe through a file descriptor. It writes up to the number of bytes specified by length from the buffer, returning the actual number of bytes written.

```rs
pub fn inherited_fds() -> Vec<u64>;
```

The child script uses this function to verify its available file descriptors. A file descriptor must -- and can only -- belong to one process. The file descriptor can be passed when using the spawn() function, as I demonstrated when introducing the spawn() function.

```rs
pub fn close(fd: u64) -> Result<(), SysError>;
```

This syscall manually closes a file descriptor. After calling it, any attempts to read from or write to the file descriptor at the other end will fail.

```rs
pub fn wait(pid: u64) -> Result<i8, SysError>;
```

The last function is wait(). The syscall pauses execution until the process specified by pid has completed.

## Errors

There are five unique errors that can be returned from the spawn family of syscalls. Most of these errors are quite self-explanatory and can occur when you pass incorrect arguments or attempt to double-close a file descriptor.

```rs
pub enum SysError {
    /// Failed to wait. Its value is 5.
    WaitFailure,
    /// Invalid file descriptor. Its value is 6.
    InvalidFd,
    /// Reading from or writing to file descriptor failed due to other end closed. Its value is 7.
    OtherEndClosed,
    /// Max vms has been spawned. Its value is 8.
    MaxVmsSpawned,
    /// Max fds has been created. Its value is 9.
    MaxFdsCreated,
}
```

Among these, a notable error is OtherEndClosed. This error allows us to implement a function like `read_all(fd) -> Vec<u8>` to read all the data from the pipe at once. Many programming languages provide similar functions in their standard libraries, and you can easily implement this functionality yourself in the ckb-vm.

```rs
pub fn read_all(fd: u64) -> Result<Vec<u8>, SysError> {
    let mut ret = Vec::new();
    let mut buf = [0; 256];
    loop {
        match syscalls::read(fd, &mut buf) {
            Ok(data) => ret.extend_from_slice(&buf[..data]),
            Err(SysError::OtherEndClosed) => break,
            Err(err) => return Err(err),
        }
    }
    Ok(ret)
}
```

## Example

Let me walk you through a basic example of how to use spawn. Suppose we want to deploy a library on the chain. This public library is quite simple; it receives input parameters, concatenates them, and returns the result to the caller. Let's see how to implement it.

The main code consists of the following four lines:

0. In the first line, we obtain the file descriptor.
0. In the second line, we gather and concatenate all the arguments.
0. In the third line, we write the result to the file descriptor.
0. Finally, we close the file descriptor.

```rs
#[no_mangle]
pub unsafe extern "C" fn main() -> u64 {
    let fds = inherited_fds();
    let out = ARGS.join("");
    write(fds[0], out.as_bytes());
    close(fds[0]);
    return 0;
}
```

So, how should we use this library? Please refer to the following code:

0. In the first line, we define the arguments to be passed to the child script.
0. In the second line, we create a pipe.
0. In the third line, we call the spawn() function, passing in the arguments and the writable file descriptor.
0. In the fourth line, we read all the data from the readable file descriptor.
0. Finally, we use the wait function to wait for the child script to exit.

```rs
#[no_mangle]
pub unsafe extern "C" fn main() -> u64 {
    let argv = ["Hello", "World!"];
    let fds = pipe();
    let pid = spawn_cell(code_hash, hash_type, &argv, &[fds[1]]);
    let data = read_all(fds[0]);
    assert_eq!(&data, b"Hello World!");
    wait(pid);
    return 0;
}
```

## Advantages of spawn

Since spawn() operates within its own memory space, independent of the parent process, it can mitigate certain security risks, particularly in scenarios involving sensitive data.

While some other blockchain virtual machines, such as the evm, also offer cross-contract call functions, these calls tend to be quite expensive, especially when invoking child contracts repeatedly. This is primarily because it requires continuously creating and destroying a virtual machine to complete each call.

```text
      +----------+
----->+ Script A +---+------+------------+------+-------+------+--------------->
      +----------+   |      ^            |      ^       |      ^
                     |      |            |      |       |      |
              Create |      | Destroy    |      |       |      |
                     v      |            v      |       v      |
                   +-+------+-+        +-+------+-+   +-+------+-+
                   | Script B |        | Script B |   | Script B |
                   +----------+        +----------+   +----------+
```

Since the ckb-vm provides a pipe implementation, this means that no matter how many times you call a child script, you only need to create and destroy the child script's execution space once.

```text
      +----------+
----->+ Script A +----+------------------+------+-------+------+-------+------->
      +----------+    |                  |      ^       |      ^       ^
                      |                  | Pipe |       | Pipe |       |
              Create  |                  |  IO  |       |  IO  |       | Destroy
                      v                  |      |       |      |       |
                   +--+-------+          v      |       v      |       |
                   | Script B |----------+------+-------+------+-------+
                   +----------+
```

## Typical Use Cases

We have envisioned several possible applications for spawn, and we believe it is particularly well-suited for certain scenarios:

- Public Library: We can use spawn to develop a common library, allowing different scripts to reuse the shared library code. This approach can simplify script development and significantly reduce deployment costs. For example, we could publish a variety of cryptographic algorithms to ckb in the form of public libraries.
- Writing Large Scripts: If your script binary size exceeds 500K, it will surpass the maximum transaction size allowed by ckb when deploying the script. In such cases, you can use spawn to split the script logic and deploy it separately.

## Conclusion

The Spawn family of functions in the ckb-vm offers an efficient, flexible, and secure method for process creation, particularly in scenarios involving complex scripts. Using spawn can significantly enhance system performance and security. By understanding and mastering the use of spawn(), developers can more effectively manage scripts while building decentralized applications.
