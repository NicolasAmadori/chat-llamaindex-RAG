import {
  getDetailContentFromFile,
  isImageFileType,
} from "@/app/client/fetch/file";
import { URLDetail, URLDetailContent, isURL } from "@/app/client/fetch/url";
import { Button } from "@/app/components/ui/button";
import { Textarea } from "@/app/components/ui/textarea";
import { useToast } from "@/app/components/ui/use-toast";
import { useSubmitHandler } from "@/app/hooks/useSubmit";
import { cn } from "@/app/lib/utils";
import { useBotStore } from "@/app/store/bot";
import { FileWrap } from "@/app/utils/file";
import { Send } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useDebouncedCallback } from "use-debounce";
import { ChatControllerPool } from "../../client/controller";
import {
  ALLOWED_DOCUMENT_EXTENSIONS,
  ALLOWED_IMAGE_EXTENSIONS,
  ALLOWED_TEXT_EXTENSIONS,
  DOCUMENT_FILE_SIZE_LIMIT,
} from "../../../constants";
import Locale from "../../locales";
import { callSession } from "../../store";
import { autoGrowTextArea } from "../../utils/autogrow";
import FileUploader from "../ui/file-uploader";
import ImagePreview from "../ui/image-preview";
import { isVisionModel } from "../../client/platforms/llm";
import "../../styles/lib/custom-theme.css";

export interface ChatInputProps {
  inputRef: React.RefObject<HTMLTextAreaElement>;
  userInput: string;
  temporaryURLInput: string;
  setUserInput: (input: string) => void;
  setTemporaryURLInput: (url: string) => void;
  scrollToBottom: () => void;
  setAutoScroll: (autoScroll: boolean) => void;
}

export default function ChatInput(props: ChatInputProps) {
  const {
    inputRef,
    userInput,
    setUserInput,
    setTemporaryURLInput,
    scrollToBottom,
    setAutoScroll,
  } = props;

  const { toast } = useToast();
  const { shouldSubmit } = useSubmitHandler();

  const botStore = useBotStore();
  const bot = botStore.currentBot();
  const session = botStore.currentSession();

  const [imageFile, setImageFile] = useState<URLDetail>();
  const [temporaryBlobUrl, setTemporaryBlobUrl] = useState<string>();

  // auto grow input
  const [inputRows, setInputRows] = useState(2);
  const measure = useDebouncedCallback(
    () => {
      const rows = inputRef.current ? autoGrowTextArea(inputRef.current) : 1;
      const inputRows = Math.min(
        20,
        Math.max(1 + Number(!false), rows),
      );
      setInputRows(inputRows);
    },
    100,
    {
      leading: true,
      trailing: true,
    },
  );

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(measure, [userInput]);

  const onInput = (text: string) => {
    setUserInput(text);
  };

  const showError = (errMsg: string) => {
    toast({
      title: errMsg,
      variant: "destructive",
    });
  };

  const callLLM = async ({
    input,
    fileDetail,
  }: {
    input?: string;
    fileDetail?: URLDetailContent;
  }) => {
    await callSession(
      bot,
      session,
      {
        onUpdateMessages: (messages) => {
          botStore.updateBotSession((session) => {
            // trigger re-render of messages
            session.messages = messages;
          }, bot.id);
        },
      },
      input,
      fileDetail,
    );
    setImageFile(undefined);
    setTemporaryURLInput("");
    setUserInput("");
  };

  const manageTemporaryBlobUrl = (
    file: File,
    action: () => Promise<void>,
  ): Promise<void> => {
    let tempUrl: string;
    if (isImageFileType(file.type)) {
      tempUrl = URL.createObjectURL(file);
      setTemporaryBlobUrl(tempUrl);
    }
    console.log("ACTION", action)
    return action().finally(() => {
      if (isImageFileType(file.type)) {
        URL.revokeObjectURL(tempUrl);
        setTemporaryBlobUrl(undefined);
      }
    });
  };


  const doSubmitFile = async (fileInput: FileWrap) => {
    try {
      const bot_id = bot.id;
      await manageTemporaryBlobUrl(fileInput.file, async () => {
        if (isImageFileType(fileInput.file.type)) {
          throw new Error("No images allowed");
        } else {
          const fileDetail = await getDetailContentFromFile(fileInput, bot_id);
        }
      });
    } catch (error) {
      console.log("ERROR", error)
      showError(Locale.Upload.Failed((error as Error).message));
    }
  };

  const doSubmit = async (input: string) => {
    console.log(botStore.currentBotId)
    if (input.trim() === "") return;
    if (isURL(input)) {
      setTemporaryURLInput(input);
    }
    await callLLM({ input, fileDetail: imageFile });
    if (!false) inputRef.current?.focus();
    setAutoScroll(true);
  };

  // check if should send message
  const onInputKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (shouldSubmit(e)) {
      if (!isRunning && !isUploadingImage) {
        doSubmit(userInput);
      }
      e.preventDefault();
    }
  };

  const autoFocus = !false; // wont auto focus on mobile screen

  let isRunning = false
  if (bot){
    isRunning = ChatControllerPool.isRunning(bot.id);
  }

  const removeImage = () => {
    setImageFile(undefined);
  };

  const previewImage = temporaryBlobUrl || imageFile?.url;
  const isUploadingImage = temporaryBlobUrl !== undefined;

  const checkExtension = (extension: string) => {
    if (!ALLOWED_DOCUMENT_EXTENSIONS.includes(extension)) {
      return Locale.Upload.Invalid(ALLOWED_DOCUMENT_EXTENSIONS.join(","));
    }
    if (
      !isVisionModel(bot.modelConfig.model) &&
      ALLOWED_IMAGE_EXTENSIONS.includes(extension)
    ) {
      return Locale.Upload.ModelDoesNotSupportImages(
        ALLOWED_TEXT_EXTENSIONS.join(","),
      );
    }
    return null;
  };

  return (
    <div>
      {botStore.currentBotId !== "-1" && (
        <div className="flex flex-1 items-end relative">
          {previewImage && (
            <div className="absolute top-3 left-3 w-12 h-12 rounded-xl cursor-pointer">
              <ImagePreview
                url={previewImage}
                uploading={isUploadingImage}
                onRemove={removeImage}
              />
            </div>
          )}
          <Textarea
            className={cn(
              "ring-inset focus-visible:ring-offset-0 pr-28 md:pr-40 min-h-[56px] shadow user-message border-none",
              {
                "pt-20": previewImage,
              }
            )}
            ref={inputRef}
            placeholder={Locale.Chat.Input}
            onInput={(e) => onInput(e.currentTarget.value)}
            value={userInput}
            onKeyDown={onInputKeyDown}
            onFocus={scrollToBottom}
            onClick={scrollToBottom}
            rows={inputRows}
            autoFocus={autoFocus}
          />
          <div className="my-2 flex items-center gap-2.5 absolute right-3.5 ">
            <Button
              className="send-button"
              onClick={() => {
                doSubmit(userInput);
                setUserInput("");
              }}
              disabled={botStore.currentBotId == "-1" || isRunning || isUploadingImage}
            >
              <Send className="h-4 w-4 mr-2" />
              {Locale.Chat.Send}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
