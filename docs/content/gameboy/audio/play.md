# GB/音频/在计算机上播放

现在我们拿到了最终的音频数据, 最后一步是通过前面提到的 cpal 库来实际在你的电脑上播放这些数据. 下面的代码片段展示了如何播放这些数据.

## 代码实现

```rs
let device = cpal::default_output_device().unwrap();
let format = device.default_output_format().unwrap();
let format = cpal::Format {
    channels: 2,
    sample_rate: format.sample_rate,
    data_type: cpal::SampleFormat::F32,
};

let event_loop = cpal::EventLoop::new();
let stream_id = event_loop.build_output_stream(&device, &format).unwrap();
event_loop.play_stream(stream_id);

let apu = Apu::power_up(format.sample_rate.0);
let apu_data = apu.buffer.clone();
mbrd.mmu.borrow_mut().apu = Some(apu);

thread::spawn(move || {
    event_loop.run(move |_, stream_data| {
        let mut apu_data = apu_data.lock().unwrap();
        if let cpal::StreamData::Output { buffer } = stream_data {
            let len = cmp::min(buffer.len() / 2, apu_data.len());
            match buffer {
                cpal::UnknownTypeOutputBuffer::F32(mut buffer) => {
                    for (i, (data_l, data_r)) in apu_data.drain(..len).enumerate() {
                        buffer[i * 2] = data_l;
                        buffer[i * 2 + 1] = data_r;
                    }
                }
                cpal::UnknownTypeOutputBuffer::U16(mut buffer) => {
                    for (i, (data_l, data_r)) in apu_data.drain(..len).enumerate() {
                        buffer[i * 2] =
                            (data_l * f32::from(std::i16::MAX) + f32::from(std::u16::MAX) / 2.0) as u16;
                        buffer[i * 2 + 1] =
                            (data_r * f32::from(std::i16::MAX) + f32::from(std::u16::MAX) / 2.0) as u16;
                    }
                }
                cpal::UnknownTypeOutputBuffer::I16(mut buffer) => {
                    for (i, (data_l, data_r)) in apu_data.drain(..len).enumerate() {
                        buffer[i * 2] = (data_l * f32::from(std::i16::MAX)) as i16;
                        buffer[i * 2 + 1] = (data_r * f32::from(std::i16::MAX)) as i16;
                    }
                }
            }
        }
    });
});
```

读者可自行将相关代码补充到 main 函数中.
