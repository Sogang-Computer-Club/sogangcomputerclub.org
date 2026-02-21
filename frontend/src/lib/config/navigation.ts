/**
 * Shared navigation configuration
 * Used by both NavigationBar and MobileMenu components
 */

export interface NavSubItem {
  name: string;
  path: string;
}

export interface NavItem {
  name: string;
  color: string;
  subItems: NavSubItem[];
}

export const navItems: NavItem[] = [
  {
    name: "About Us",
    color: "#AE1F1F",
    subItems: [
      { name: "인사말", path: "/about-us/welcome" },
      { name: "활동/행사", path: "/about-us/activity" },
      { name: "SNS", path: "/about-us/SNS" },
    ],
  },
  {
    name: "Notice",
    color: "#AE1F1F",
    subItems: [
      { name: "공지", path: "/notice/announcements" },
      { name: "동아리방", path: "/notice/lighthouse" },
      { name: "달력", path: "/notice/calendar" },
      { name: "모집 안내", path: "/notice/recruitment" },
    ],
  },
  {
    name: "Community",
    color: "#AE1F1F",
    subItems: [
      { name: "미디어관", path: "/community/media" },
      { name: "피드", path: "/community/feed" },
    ],
  },
  {
    name: "Study",
    color: "#AE1F1F",
    subItems: [{ name: "Study", path: "/study" }],
  },
  {
    name: "Library",
    color: "#AE1F1F",
    subItems: [{ name: "SGCS Library", path: "/library" }],
  },
];
