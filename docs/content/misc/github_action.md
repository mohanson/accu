# 杂项/Github Action 配置编写

Github action 是 github 提供的一种持续集成和持续部署工具, 可以帮助开发者自动化构建, 测试和部署代码. 通过编写 github action 配置文件, 可以定义在特定事件发生时自动执行的工作流程.

配置文件必须位于 `.github/workflows` 目录下, 文件名可以自定义, 但必须以 `.yml` 或 `.yaml` 结尾. 常见的目录结构如下:

```text
.github/workflows
├── develop.yaml
└── release.yaml
```

## 事件触发

我们可以通过以下链接查看 github action 支持的事件触发类型, 包含 push, pull_request, release 等等. 选择合适的事件触发类型可以帮助我们更好地管理和自动化我们的项目.

<https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>

## 我的模板

这是我的一份常用配置模板, 模板基于 golang 项目, 你可以根据自己的项目需求进行修改和调整.

**develop.yaml**: 主要用于开发的 CI/CD 配置, 包含构建和测试步骤.

```yaml
name: develop

on:
  pull_request:
    types:
      - opened
  push:

jobs:
  develop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-go@v6
        with:
          go-version: '1.26'
      - name: Make
        run: |
          bash cmd/develop.sh
      - name: Test
        run: |
          go test -v -p 1 ./...
```

**release.yaml**: 主要用于发布的 CI/CD 配置, 包含构建和发布步骤. 当有新的 release 被创建时, 这个配置会自动执行, 构建项目并将构建产物上传到 github release 中.

```yaml
name: release

on:
  release:
    types:
      - created

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-go@v6
        with:
          go-version: '1.26'
      - name: Make
        run: |
          bash cmd/release.sh
      - name: Push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release upload ${{ github.ref_name }} bin/release/daze_darwin_amd64.zip
          gh release upload ${{ github.ref_name }} bin/release/daze_darwin_arm64.zip
          gh release upload ${{ github.ref_name }} bin/release/daze_android_arm64.zip
          gh release upload ${{ github.ref_name }} bin/release/daze_linux_amd64.zip
          gh release upload ${{ github.ref_name }} bin/release/daze_windows_amd64.zip
```

## 修改环境变量 PATH

在 github action 中, 可以通过修改环境变量 PATH 来添加新的路径. 这样可以让我们在工作流程中直接使用这些路径下的命令. 我们可以添加以下步骤来修改 PATH, 把 `${{ github.workspace }}/bin` 添加到 PATH 中, 这样我们就可以直接使用 `${{ github.workspace }}/bin` 目录下的命令了.

```yaml
echo ${{ github.workspace }}/bin >> ${{ github.path }}
```

这里要注意, 对于 github action 中每一个步骤来说, 环境变量 PATH 都是唯一的. 也就是说, 在一个步骤中修改 PATH 并不会影响到该步骤后续的命令, 只会影响到该步骤的后续步骤.

## 常见 Action 模块

- [actions/checkout@v6](https://github.com/actions/checkout)
- [actions/setup-go@v6](https://github.com/actions/setup-go)
- [actions/setup-python@v6](https://github.com/actions/setup-python)
- [actions-rust-lang/setup-rust-toolchain@v1](https://github.com/actions-rust-lang/setup-rust-toolchain)
