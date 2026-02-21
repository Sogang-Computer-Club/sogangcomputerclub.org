import { redirect } from "@sveltejs/kit";
import type { MediaSummary } from "$lib";
import type { PageServerLoad } from "./$types";
import allMedia from "$lib/data/media_data.json";

const POSTS_PER_PAGE = 12;

export const load: PageServerLoad = async ({ url }) => {
  const pageParam = url.searchParams.get("page");
  const currentPage = parseInt(pageParam) || 1;
  const totalPages = Math.ceil(allMedia.length / POSTS_PER_PAGE);

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
  const slicedMediaSummary: MediaSummary[] = allMedia.slice(
    offset,
    offset + POSTS_PER_PAGE,
  );

  return { currentPage, totalPages, slicedMediaSummary };
};
