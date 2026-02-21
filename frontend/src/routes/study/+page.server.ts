import type { PageServerLoad } from "./$types.js";
import { getMemos } from "$lib/api";

export const load: PageServerLoad = async () => {
  try {
    let memos = await getMemos();
    return { memos: memos };
  } catch (error) {
    console.error("Failed to load memos on server:", error);
    return { memos: [] };
  }
};
