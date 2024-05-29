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
  author: string;
  date: string | null;
};

const sources: Source[] = [
  {
    link: "https://example.com/article1",
    text: "An interesting article about technology.",
    author: "John Doe",
    date: "2023-01-01",
  },
  {
    link: "https://example.com/article2",
    text: "A comprehensive guide on software development.",
    author: "Jane Smith",
    date: "2023-02-15",
  },
  {
    link: "https://example.com/article3",
    text: "An analysis of modern web design trends.",
    author: "Alice Johnson",
    date: null,
  },
];

export function BotSideBar(props: { className?: string }) {
  return (
    <div className="h-full relative group border-r w-full md:w-[25%] border-l">
      <div className="w-full h-full p-5 flex flex-col gap-5">
        <div className="flex flex-col flex-1">
          <div className="mb-5 flex justify-center gap-5 items-start">
            <Typography.H1>{Locale.Home.Source}</Typography.H1>
          </div>
          <ScrollArea className="h-full pr-0 md:pr-3">
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