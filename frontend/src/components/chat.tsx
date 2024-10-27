"use client";

import {
  ChatBubble,
  ChatBubbleAvatar,
  ChatBubbleMessage,
} from "@/components/ui/chat/chat-bubble";
import { ChatInput } from "@/components/ui/chat/chat-input";
import { ChatMessageList } from "@/components/ui/chat/chat-message-list";
import { Button } from "@/components/ui/button";
import { CornerDownLeft } from "lucide-react";
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
const model = genAI.getGenerativeModel({
  model: "gemini-1.5-flash",
  systemInstruction:
    "You are a friendly, supportive virtual therapist. Respond naturally to the user, reacting in a way that feels conversational and empathetic, without sounding overly formal or prescriptive. If the user mentions feelings or emotions, reflect on those in a gentle and friendly way. However, if they are joking or using casual language, respond in kind, maintaining a balance between supportiveness and a sense of humor. Encourage them to explore their thoughts when appropriate but keep it light and adaptive to the context they present. Ask questions to the user for them to open up!",
});

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const startingMessage = "How are you doing?";
  const [isGenerating, setIsGenerating] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: startingMessage },
  ]);
  const [input, setInput] = useState("");
  const [keystrokes, setKeystrokes] = useState<number>(0);
  const [backspaces, setBackspaces] = useState<number>(0);
  const [typingStartTime, setTypingStartTime] = useState<number | null>(null);
  const [typingSpeed, setTypingSpeed] = useState<number>(0); // words per minute

  const messagesRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (typingStartTime === null) {
        setTypingStartTime(Date.now());
      }

      if (event.key === "Backspace") {
        setBackspaces((prev) => prev + 1);
      } else {
        setKeystrokes((prev) => prev + 1);
      }
    };

    const calculateTypingSpeed = () => {
      if (typingStartTime !== null) {
        const elapsedTime = (Date.now() - typingStartTime) / 60000; // Convert to minutes
        const wordsTyped = keystrokes / 5; // Approx. 5 characters per word
        setTypingSpeed(wordsTyped / elapsedTime);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    // Cleanup event listener
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      calculateTypingSpeed();
    };
  }, [keystrokes, backspaces, typingStartTime]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsGenerating(true);

    try {
      const context = updatedMessages
        .map(
          (msg) =>
            `${msg.role === "user" ? "User" : "Assistant"}: ${msg.content}`
        )
        .join("\n");

      const result = await model.generateContent(context);
      const aiMessage: Message = {
        role: "assistant",
        content: result.response.text(),
      };

      const finalMessages = [...updatedMessages, aiMessage];
      setMessages(finalMessages);
      console.log("aiMessage.content", aiMessage.content);

      const question =
        messages.length > 1
          ? messages[messages.length - 1].content
          : startingMessage;
      const answer = input;

      console.log(keystrokes, backspaces, typingSpeed);
      const previousAIMessage =
        messages.length > 1
          ? messages[messages.length - 1].content
          : startingMessage;

      await fetch("http://localhost:8000/api/messages/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          response: answer,
          previous_ai_message: previousAIMessage,
          typing_metrics: {
            keystrokes,
            backspaces,
            typing_speed: typingSpeed,
          },
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (error) {
      console.error("Error generating response:", error);
    } finally {
      setIsGenerating(false);
      // Reset typing metrics
      setKeystrokes(0);
      setBackspaces(0);
      setTypingStartTime(null);
      setTypingSpeed(0);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (isGenerating || !input) return;
      setIsGenerating(true);
      handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
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
                      {!isGenerating && <></>}
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
            disabled={!input}
            type="submit"
            size="sm"
            className="ml-2 gap-1.5 flex align-center mr-2"
          >
            Send Message
            <CornerDownLeft className="size-3.5" />
          </Button>
        </form>
      </div>
    </main>
  );
}
