import allPosts from "$lib/data/posts.json";
import { redirect } from "@sveltejs/kit";
import type { PostSummary } from "$lib";
import type { PageServerLoad } from "./$types";

const POSTS_PER_PAGE = 10;

export const load: PageServerLoad = async ({ url }) => {
  const pageParam = url.searchParams.get("page");
  const currentPage = parseInt(pageParam) || 1;
  const totalPages = Math.ceil(allPosts.length / POSTS_PER_PAGE);

  if (Number(pageParam) != currentPage) {
    const newUrl = new URL(url);
    newUrl.searchParams.set("page", currentPage.toString());
    throw redirect(307, newUrl.toString());
  }

  if (currentPage < 1) {
    const newUrl = new URL(url);
    newUrl.searchParams.set("page", "1");
    throw redirect(307, newUrl.toString());
  } else if (currentPage > totalPages) {
    const newUrl = new URL(url);
    newUrl.searchParams.set("page", totalPages.toString());
    throw redirect(307, newUrl.toString());
  }

  const offset = (currentPage - 1) * POSTS_PER_PAGE;
  const slicedPostSummary: PostSummary[] = allPosts.slice(
    offset,
    offset + POSTS_PER_PAGE,
  );

  return { currentPage, totalPages, slicedPostSummary };
};
