# Solana/更多开发者工具/web3.js 的常见坑与规避

这里汇总一下我在使用 solana/web3.js + 浏览器钱包 phantom 开发时容易踩到的问题与解决方案. 下面这些问题都是我实际遇到过的, 并且花了不少时间调试才搞明白.

## Phantom 钱包的运行环境

Phantom 钱包仅在两种来源下工作:

- `localhost`(http/https 均可)
- `https` 站点(必须是安全源)

在非 https 的远程域名下, phantom 不会注入到浏览器环境里, 您无法连接到 phantom 钱包.

## 官方公共 rpc 的 cors / 403

直接从浏览器请求 `https://api.mainnet-beta.solana.com` 常见 403 或 cors 拒绝. 此问题的原因是官方公共 rpc 主动限制了浏览器的访问. 要解决此问题, 有两种做法:

0. 使用允许浏览器访问, 带 api key 的提供商 rpc, 作者采用了此方式并使用了 helius.
0. 或者在开发服务器/后端配置反向代理, 让前端走同源路径.

Vite 代理示例:

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/rpc': {
        target: 'https://your.provider.rpc/solana-mainnet?api-key=XXXX',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
```

前端代码中使用相对地址:

```ts
const RPC_ENDPOINT = import.meta.env.VITE_SOLANA_RPC || '/rpc'
```

## 交易体积限制

Solana 交易大小上限为 1232 字节, 排除掉签名等开销, 实际可用空间更少. 如果您在交易中携带了大量数据, 可能会遇到 `Transaction too large` 错误.
