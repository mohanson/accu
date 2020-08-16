# Go 监听目录

在许多情景下, 我们需要有一种方式监听目录内的文件变化: 在开发 web 应用时, 修改源码后自动重启服务器; 修改源码后自动重新编译; 修改文件后自动上传文件至远端服务器等.

对于 windows, 几乎所有目录监听程序使用的都是 Windows API 中的 `ReadDirectoryChangesW` 函数. 在本文之前, 使用 Golang 完成目录监听已经有部分轮子了, 但是无一例外这些轮子对文件系统事件进行了过度封装, 决定自己动手~

```go
package main

import (
	"log"
	"syscall"
	"unsafe"
)

type FileNotifyInformation struct {
	Action uint32
	Name   string
}

func Fswatch(path string) (chan FileNotifyInformation, error) {
	handle, err := syscall.CreateFile(
		syscall.StringToUTF16Ptr(path),
		0x0001,
		syscall.FILE_SHARE_READ|syscall.FILE_SHARE_WRITE|syscall.FILE_SHARE_DELETE,
		nil,
		syscall.OPEN_EXISTING,
		syscall.FILE_FLAG_BACKUP_SEMANTICS,
		0,
	)
	if err != nil {
		return nil, err
	}

	c := make(chan FileNotifyInformation, 4)
	go func() {
		defer syscall.CloseHandle(handle)
		defer close(c)
		buflen := 1024
		buf := make([]byte, buflen)
		for {
			err := syscall.ReadDirectoryChanges(
				handle,
				&buf[0],
				uint32(buflen),
				true,
				syscall.FILE_NOTIFY_CHANGE_FILE_NAME|
					syscall.FILE_NOTIFY_CHANGE_DIR_NAME|
					syscall.FILE_NOTIFY_CHANGE_ATTRIBUTES|
					syscall.FILE_NOTIFY_CHANGE_SIZE|
					syscall.FILE_NOTIFY_CHANGE_LAST_WRITE,
				nil,
				&syscall.Overlapped{},
				0,
			)
			if err != nil {
				break
			}

			var offset uint32
			for {
				raw := (*syscall.FileNotifyInformation)(unsafe.Pointer(&buf[offset]))
				buf := (*[syscall.MAX_PATH]uint16)(unsafe.Pointer(&raw.FileName))
				name := syscall.UTF16ToString(buf[:raw.FileNameLength/2])
				info := FileNotifyInformation{
					Action: raw.Action,
					Name:   name,
				}
				c <- info
				if raw.NextEntryOffset == 0 {
					break
				}
				offset += raw.NextEntryOffset
				if offset >= 1024 {
					break
				}
			}
		}
	}()
	return c, nil
}

func main() {
	c, err := Fswatch("/tmp")
	if err != nil {
		log.Fatalln(err)
	}
	for info := range c {
		switch info.Action {
		case 1:
			log.Println("Create", info.Name)
		case 2:
			log.Println("Delete", info.Name)
		case 3:
			log.Println("Update", info.Name)
		case 4:
			log.Println("RenameFrom", info.Name)
		case 5:
			log.Println("RenameTo", info.Name)
		}

	}
}
```

上面的代码监听了 "/tmp" 目录下的文件系统事件, 如果对目录内的对象做了任何修改, 就可以看见对应的输出.
