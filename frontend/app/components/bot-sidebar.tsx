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
    <div className="h-full relative group border-r w-full md:w-[30%] border-l">
      <div className="w-full h-full p-5 flex flex-col gap-5">
        <div className="flex flex-col flex-1 overflow-hidden">
          <div className="mb-5 flex justify-center gap-5 items-start">
            <Typography.H1>{Locale.Home.SideBar.Title}</Typography.H1>
          </div>
          <ScrollArea className="flex-1">
            {sources.map((s) => (
              <SourceItem source={s} />
            ))}
          </ScrollArea>
        </div>
        <div className="flex items-center justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.open(GITHUB_URL, "_blank")}
          >
            <Github className="mr-2 h-4 w-4" />
            <span>{Locale.Home.Github}</span>
          </Button>
        </div>
      </div>
    </div>
  );
}