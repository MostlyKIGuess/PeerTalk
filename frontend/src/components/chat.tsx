"use client";

import {
  ChatBubble,
  ChatBubbleAction,
  ChatBubbleAvatar,
  ChatBubbleMessage,
} from "@/components/ui/chat/chat-bubble";
import { ChatInput } from "@/components/ui/chat/chat-input";
import { ChatMessageList } from "@/components/ui/chat/chat-message-list";
import { Button } from "@/components/ui/button";
import {
  CopyIcon,
  CornerDownLeft,
  RefreshCcw,
  Volume2,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CodeDisplayBlock from "@/components/code-display-block";
import { GoogleGenerativeAI } from "@google/generative-ai";




const geminiApiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
if (!geminiApiKey) {
  throw new Error("NEXT_PUBLIC_GEMINI_API_KEY is not defined");
}
const genAI = new GoogleGenerativeAI(geminiApiKey);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash",
    systemInstruction: "You are a friendly, supportive virtual therapist. Respond naturally to the user, reacting in a way that feels conversational and empathetic, without sounding overly formal or prescriptive. If the user mentions feelings or emotions, reflect on those in a gentle and friendly way. However, if they are joking or using casual language, respond in kind, maintaining a balance between supportiveness and a sense of humor. Encourage them to explore their thoughts when appropriate but keep it light and adaptive to the context they present.Ask questions to the user for them to open up!"
 });

const ChatAiIcons = [
  {
    icon: CopyIcon,
    label: "Copy",
  },
  {
    icon: RefreshCcw,
    label: "Refresh",
  },
  {
    icon: Volume2,
    label: "Volume",
  },
];

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "How are you doing?" },
  ]);
  const [input, setInput] = useState("");
  const [isLoading] = useState(false);

  const messagesRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages([...messages, userMessage]);
    setInput("");
    setIsGenerating(true);

    // const promptText = "You are a compassionate and reflective virtual therapist. Guide the user gently through their thoughts and feelings without asking any direct questions. Encourage them to share more by validating their emotions and offering gentle, open-ended reflections. Focus on empathy and active listening, helping the user explore their experiences in a supportive and non-intrusive way. Emphasize phrases like ‘It sounds like…’ or ‘It seems as if...’ to promote a safe, judgment-free environment where they feel heard and understood. ";
    const modifiedInput = `${input}`;

    try {
        const result = await model.generateContent(modifiedInput);
        const aiMessage: Message = { role: "assistant", content: result.response.text() };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (error) {
        console.error("Error generating response:", error);
    } finally {
        setIsGenerating(false);
    }
};


  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (isGenerating || isLoading || !input) return;
      setIsGenerating(true);
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
    }
  };

  const handleActionClick = async (action: string, messageIndex: number) => {
    console.log("Action clicked:", action, "Message index:", messageIndex);
    if (action === "Refresh") {
      setIsGenerating(true);
      try {
        const message = messages[messageIndex];
        const result = await model.generateContent(message.content);
        const aiMessage: Message = { role: "assistant", content: result.response.text() };
        setMessages((prevMessages) => {
          const newMessages = [...prevMessages];
          newMessages[messageIndex] = aiMessage;
          return newMessages;
        });
      } catch (error) {
        console.error("Error reloading:", error);
      } finally {
        setIsGenerating(false);
      }
    }

    if (action === "Copy") {
      const message = messages[messageIndex];
      if (message && message.role === "assistant") {
        navigator.clipboard.writeText(message.content);
      }
    }
  };

  return (
    <main className="flex h-screen w-full max-w-3xl flex-col items-center mx-auto py-6">
      <ChatMessageList ref={messagesRef}>
        {/* Initial Message */}
        {messages.length === 1 && (
          <div className="w-full bg-background shadow-sm border rounded-lg p-8 flex flex-col gap-2">
            <h1 className="font-bold">Welcome to PeerTalk.</h1>
            <p className="text-muted-foreground text-sm">
              Talk with your AI assistant about anything you want. Just start
            </p>
          </div>
        )}

        {/* Messages */}
        {messages &&
          messages.map((message, index) => (
            <ChatBubble
              key={index}
              variant={message.role == "user" ? "sent" : "received"}
            >
              <ChatBubbleAvatar
                src=""
                fallback={message.role == "user" ? "👨🏽" : "🤖"}
              />
              <ChatBubbleMessage>
                {message.content
                  .split("```")
                  .map((part: string, index: number) => {
                    if (index % 2 === 0) {
                      return (
                        <Markdown key={index} remarkPlugins={[remarkGfm]}>
                          {part}
                        </Markdown>
                      );
                    } else {
                      return (
                        <pre className="whitespace-pre-wrap pt-2" key={index}>
                          <CodeDisplayBlock code={part} lang="" />
                        </pre>
                      );
                    }
                  })}

                {message.role === "assistant" &&
                  messages.length - 1 === index && (
                    <div className="flex items-center mt-1.5 gap-1">
                      {!isGenerating && (
                        <>
                          {ChatAiIcons.map((icon, iconIndex) => {
                            const Icon = icon.icon;
                            return (
                              <ChatBubbleAction
                                variant="outline"
                                className="size-5"
                                key={iconIndex}
                                icon={<Icon className="size-3" />}
                                onClick={() =>
                                  handleActionClick(icon.label, index)
                                }
                              />
                            );
                          })}
                        </>
                      )}
                    </div>
                  )}
              </ChatBubbleMessage>
            </ChatBubble>
          ))}

        {/* Loading */}
        {isGenerating && (
          <ChatBubble variant="received">
            <ChatBubbleAvatar src="" fallback="🤖" />
            <ChatBubbleMessage isLoading />
          </ChatBubble>
        )}
      </ChatMessageList>
      <div className="w-full px-4">
        <form
          ref={formRef}
          onSubmit={handleSubmit}
          className="relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring flex items-center"
        >
          <ChatInput
            value={input}
            onKeyDown={onKeyDown}
            onChange={handleInputChange}
            placeholder="Type your message here..."
            className="min-h-12 resize-none rounded-lg bg-background border-0 p-3 shadow-none focus-visible:ring-0 flex-grow"
          />
          <Button
            disabled={!input || isLoading}
            type="submit"
            size="sm"
            className="ml-2 gap-1.5 flex align-center"
          >
            Send Message
            <CornerDownLeft className="size-3.5" />
          </Button>
        </form>
      </div>
    </main>
  );
}