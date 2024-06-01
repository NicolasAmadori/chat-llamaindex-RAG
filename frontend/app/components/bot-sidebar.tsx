import { ThemeToggle } from "@/app/components/layout/theme-toggle";
import { Github, Settings } from "lucide-react";
import dynamic from "next/dynamic";
import { useNavigate } from "react-router-dom";
import { GITHUB_URL, Path } from "../../constants";
import Locale from "../locales";
import { Button } from "./ui/button";
import Typography from "./ui/typography";
import { useSidebarContext } from "@/app/components/home";
import { ScrollArea } from "./ui/scroll-area";
import SourceItem from "./source-item";
import "../styles/lib/custom-theme.css";

export type Source = {
  link: string;
  text: string;
  startHighlight: number;
  endHighlight: number;
  author: string;
  date: string | null;
};

const sources: Source[] = [
  {
    link: "https://example.com/article1",
    text: "An interesting article about technology. This piece delves into the latest advancements in artificial intelligence, exploring how AI is transforming various industries. The author discusses the ethical considerations and potential future developments, providing a comprehensive overview of the current state of technology.",
    author: "John Doe",
    date: "2023-01-01",
    startHighlight: 33,
    endHighlight: 94
  },
  {
    link: "https://example.com/article2",
    text: "A comprehensive guide on software development. This guide covers the fundamental principles of software engineering, including best practices for coding, debugging, and testing. It also explores advanced topics such as agile methodologies, continuous integration, and the latest tools and frameworks used by professionals in the field.",
    author: "Jane Smith",
    date: "2023-02-15",
    startHighlight: 9,
    endHighlight: 88
  },
  {
    link: "https://example.com/article3",
    text: "An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends. An analysis of modern web design trends. An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends.An analysis of modern web design trends. This article examines the latest trends in web design, including the move towards minimalism, the use of bold typography, and the increasing importance of mobile-first design. The author also discusses the impact of user experience (UX) and user interface (UI) design on the success of websites and applications.",
    author: "Alice Johnson",
    date: "2023-02-15",
    startHighlight: 1450,
    endHighlight: 1800
  },
];

export function BotSideBar(props: { className?: string }) {
  return (
    <div className={`h-full relative group w-full md:w-[30%] shadow-lg ${props.className} side-bar`}>
      <div className="w-full h-full p-5 flex flex-col gap-5">
        <div className="flex flex-col flex-1 overflow-hidden">
          <div className="mb-2 flex justify-center items-start">
            <Typography.H2>{Locale.Home.SideBar.Title}</Typography.H2>
          </div>
          <ScrollArea className="flex-1">
            {sources.map((s) => (
              <SourceItem source={s} />
            ))}
          </ScrollArea>
        </div>
      </div>
    </div>
  );
}