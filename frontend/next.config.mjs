import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n.ts");

/** @type {import('next').NextConfig} */
export default withNextIntl({
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.greenhouse.io" },
      { protocol: "https", hostname: "**.lever.co" },
      { protocol: "https", hostname: "**.ashbyhq.com" },
    ],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
});
