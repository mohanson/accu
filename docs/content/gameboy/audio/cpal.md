# GB/音频/Rust Cpal 库介绍

对于数字音频来说, 通常其波形是已知的, 这在 Game Boy 中也不例外. 为了在 PC 上播放这些波形图所代表的音频, 需要能将波形数据推送到音频设备(例如音响, 耳机等)的手段.

cpal 是 Rust 下的一个底层音频 IO 库, 通过它可以播放(到音频设备)和收集音频流(从耳麦). 本小节将聚焦在使用 cpal 播放音频上. 在 cpal 中有以下几个概念:

1. Device. Device 是一个音频设备, 该设备能提供音频输入流, 音频输出流或两者兼备. 常见比如麦克风, 音响, 耳麦等, 都是合法的 Device.
2. Stream. Stream 是开放的音频通道. Input streams 允许你接收音频数据, Ouput streams 允许你播放音频数据. 在创建新的 streams 的时候, 必须指定要处理该 stream 的 device.
3. EventLoop. EventLoop 是由一个或多个设备运行的流的集合. 每个流必须属于 EventLoop, 并且属于 EventLoop 的所有流都是一起管理的.

使用 cpal 的第一步是创建一个 EventLoop:

```rs
use cpal::EventLoop;

let event_loop = EventLoop::new();
```

然后需要选择一个播放设备. 最简单的方法是通过 cpal::default_output_device() 函数使用默认输出设备, 这通常与当前操作系统设置的默认音频播放设备一样. 或者, 可以使用 devices() 函数枚举所有可用设备. 请注意, 如果系统上没有可用于该流类型的设备, 则 default_output_device() 函数将会返回 None.

```rs
let device = cpal::default_output_device().expect("no output device available");
```

在创建 Stream 之前, 必须先行决定音频样本的格式. 使用 cpal::supported_output_formats() 方法查询所有支持的格式. 它生成一个 SupportedFormat 结构列表, 在之后可以将其转换为实际的 Format 结构. 除了查询格式列表再选择合适的格式外, 也可以手动构建自己的格式, 但如果设备不支持该格式, 则在构建流时可能会导致错误, 因此后者并不推荐使用. 注意, supported_output_formats() 方法可能会返回错误, 例如, 当设备已断开连接的时候.

```rs
let mut supported_formats_range = device.supported_output_formats()
    .expect("error while querying formats");
let format = supported_formats_range.next()
    .expect("no supported format?!")
    .with_max_sample_rate();
```

为了创建 Stream 所需要的所有内容均已准备就绪, 现在从 EventLoop 中创建它:

```rs
let stream_id = event_loop.build_output_stream(&device, &format).unwrap();
```

build_output_stream() 返回的值是一个 StreamId, 通过该 StreamId 可以控制流的运行细节. 现在可以安全的启动流了, 通过 EventLoop 上的 play_stream() 方法完成它:

```rs
event_loop.play_stream(stream_id);
```

音频设备正在等待你传入数据! 在 event_loop 上调用 run() 来开始处理:

```rs
event_loop.run(move |_stream_id, _stream_data| {
    // read or write stream data here
});
```

当 run() 运行时, 指定的音频设备将定期调用我们传递给此函数的回调函数. 回调函数接收 StreamId 和 StreamData 类型的实例, 可以从该实例读取或写入的数据. StreamData 的数据类型可以是 I16, U16 或 F32 中的一个, 具体取决于传递给build_output_stream的格式.

在下面这个例子中, 程序会输出一个正弦波, 运行后将能听到"哔哔"的声音. 完整代码如下所示:

```rs
use cpal;

fn main() {
    let device = cpal::default_output_device().expect("Failed to get default output device");
    let format = device.default_output_format().expect("Failed to get default output format");
    let event_loop = cpal::EventLoop::new();
    let stream_id = event_loop.build_output_stream(&device, &format).unwrap();
    event_loop.play_stream(stream_id.clone());

    let sample_rate = format.sample_rate.0 as f32;
    let mut sample_clock = 0f32;

    // Produce a sinusoid of maximum amplitude.
    let mut next_value = || {
        sample_clock = (sample_clock + 1.0) % sample_rate;
        (sample_clock * 440.0 * 2.0 * 3.141592 / sample_rate).sin()
    };

    event_loop.run(move |_, data| {
        match data {
            cpal::StreamData::Output { buffer: cpal::UnknownTypeOutputBuffer::U16(mut buffer) } => {
                for sample in buffer.chunks_mut(format.channels as usize) {
                    let value = ((next_value() * 0.5 + 0.5) * std::u16::MAX as f32) as u16;
                    for out in sample.iter_mut() {
                        *out = value;
                    }
                }
            },
            cpal::StreamData::Output { buffer: cpal::UnknownTypeOutputBuffer::I16(mut buffer) } => {
                for sample in buffer.chunks_mut(format.channels as usize) {
                    let value = (next_value() * std::i16::MAX as f32) as i16;
                    for out in sample.iter_mut() {
                        *out = value;
                    }
                }
            },
            cpal::StreamData::Output { buffer: cpal::UnknownTypeOutputBuffer::F32(mut buffer) } => {
                for sample in buffer.chunks_mut(format.channels as usize) {
                    let value = next_value();
                    for out in sample.iter_mut() {
                        *out = value;
                    }
                }
            },
            _ => (),
        }
    });
}
```
