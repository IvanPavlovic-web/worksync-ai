import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { serverFetch } from "@/lib/api";

interface Post {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  content_html: string;
  category: string;
  keywords?: string[];
  seo_title?: string;
  seo_description?: string;
  published_at: string;
  updated_at: string;
}

async function getPost(slug: string) {
  return serverFetch<Post>(`/blog/${slug}`, 3600);
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = await getPost(params.slug);
  if (!post) return { title: "Post nije naÄ‘en" };
  return {
    title: post.seo_title || post.title,
    description: post.seo_description || post.excerpt,
    keywords: post.keywords,
    alternates: { canonical: `/blog/${post.slug}` },
    openGraph: {
      title: post.seo_title || post.title,
      description: post.seo_description || post.excerpt,
      type: "article",
      publishedTime: post.published_at,
      modifiedTime: post.updated_at,
    },
  };
}

export default async function BlogPostPage({
  params,
}: {
  params: { slug: string };
}) {
  const post = await getPost(params.slug);
  if (!post) notFound();

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.excerpt,
    datePublished: post.published_at,
    dateModified: post.updated_at,
    author: { "@type": "Organization", name: "WorkSync" },
    publisher: {
      "@type": "Organization",
      name: "WorkSync",
      logo: { "@type": "ImageObject", url: "/logo.png" },
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": `/blog/${post.slug}` },
  };

  const breadcrumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "PoÄetna", item: "/" },
      { "@type": "ListItem", position: 2, name: "Blog", item: "/blog" },
      {
        "@type": "ListItem",
        position: 3,
        name: post.title,
        item: `/blog/${post.slug}`,
      },
    ],
  };

  return (
    <article className="max-w-3xl mx-auto px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbs) }}
      />

      <header className="mb-8">
        <p className="text-sm text-slate-500 mb-2">
          {new Date(post.published_at).toLocaleDateString("bs-BA")} Â·{" "}
          {post.category}
        </p>
        <h1 className="text-4xl font-bold leading-tight">{post.title}</h1>
        <p className="text-slate-400 mt-3 text-lg">{post.excerpt}</p>
      </header>

      <div
        className="prose prose-invert prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: post.content_html }}
      />

      <div className="mt-12 pt-8 border-t border-slate-800">
        <p className="text-slate-400 text-sm">
          TraÅ¾iÅ¡ posao?{" "}
          <a href="/poslovi" className="text-indigo-400 hover:underline">
            Pogledaj {">"}500 aktivnih oglasa
          </a>{" "}
          na WorkSync-u.
        </p>
      </div>
    </article>
  );
}

