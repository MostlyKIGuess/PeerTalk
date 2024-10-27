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
import {  useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CodeDisplayBlock from "@/components/code-display-block";
import { GoogleGenerativeAI } from "@google/generative-ai";

const geminiApiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
if (!geminiApiKey) {
  throw new Error("NEXT_PUBLIC_GEMINI_API_KEY is not defined");
}

const genAI = new GoogleGenerativeAI(geminiApiKey);

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
  const [isLoading] = useState(false);

  const messagesRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const [session0, setSession0] = useState(false);
  const [last_session_recommendation, setLastSessionRecommendation] =
    useState("");
  const [last_session_persona, setLastSessionPersona] = useState("");

  const getSystemInstruction = (isReturningUser: boolean) => {
    return isReturningUser
      ? `You are a friendly, supportive virtual therapist. Respond naturally to the user, reacting in a way that feels conversational and empathetic, without sounding overly formal or prescriptive. If the user mentions feelings or emotions, reflect on those in a gentle and friendly way. However, if they are joking or using casual language, respond in kind, maintaining a balance between supportiveness and a sense of humor. Encourage them to explore their thoughts when appropriate but keep it light and adaptive to the context they present. Ask questions to the user for them to open up! \nHere is the persona of the user based on the last conversation: ${last_session_persona} \nHere is the recommendation we had given them in the last session: ${last_session_recommendation}. \nTry to align the questions in terms of working on the recommendations and trying to help them with any mental health realted issues based on their persona. If the last response seems to be irrelevent, let them know that the converstaion is not moving in the intended direction and ask them to provide more context.`
      : "You are a friendly, supportive virtual therapist. Respond naturally to the user, reacting in a way that feels conversational and empathetic, without sounding overly formal or prescriptive. If the user mentions feelings or emotions, reflect on those in a gentle and friendly way. However, if they are joking or using casual language, respond in kind, maintaining a balance between supportiveness and a sense of humor. Encourage them to explore their thoughts when appropriate but keep it light and adaptive to the context they present. Ask questions to the user for them to open up! Here are the list of questions you should ask in this conversation: - How do you typically relax after a busy day? \n- How have you been feeling about your workload lately? Any moments of joy or stress? \n- What do you usually do to unwind after a long day? Any favorite activities or routines? \n- How do you usually spend time with friends or classmates? Any recent hangouts or events? \n- When you feel upset or stressed, what helps you feel better? \n- What do you think about the spaces you spend time in, like school or home? Do they feel comfortable for you? \n- What are some habits you're proud of? \n- What have you done recently that you are most proud of? \n- Where is your happy place? \n- Who makes you feel happy and what is it about them that's so special? \n- What cheers you up? \n- What's something new you'd like to try? \n- What's one thing you wish people understood about you? \n- What were your high and low moments this week? \n-  Is there anything about your day or week that stands out? \nBelow is a list of questions and answers that have already been asked. Do not repeat any of the questions. Ask the most appropriate question based on the conversation from the above list. If the last response seems to be irrelevent, let them know that the converstaion is not moving in the intended direction and ask them to provide more context";
  };

  // api call to /api/startsession
  useEffect(() => {
    fetch("http://localhost:8000/api/startsession", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setSession0(data.oldUser);
        setLastSessionRecommendation(data.recommendation);
        setLastSessionPersona(data.final_persona);
      })
      .catch((error) => console.error("Fetch error:", error));
  }, []);

  const model = genAI.getGenerativeModel({
    model: "gemini-1.5-flash",
    systemInstruction: getSystemInstruction(session0),
  });

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

      await fetch("http://localhost:8000/api/messages/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          response: answer,
          timestamp: new Date().toISOString(),
        }),
      });
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
            disabled={!input || isLoading}
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
