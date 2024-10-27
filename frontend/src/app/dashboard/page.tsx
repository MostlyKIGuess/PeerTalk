"use client";
import "./page.css";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useState, useEffect, ReactNode } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

type Message = {
  question: string;
  response: string;
  metrics: {
    polarity: string;
    keywords: string[];
    concerns: { [name: string]: number };
    keystrokes: number;
    backspaces: number;
    speed: number;
  };
  timestamp: string;
};

type Session = {
  start_time: string;
  messages: Message[];
  recommendation: string;
  final_persona: string;
  metrics: {
    speed: ReactNode;
    backspaces: ReactNode;
    keystrokes: ReactNode;
    polarity: string;
    keywords: string[];
    concerns: { [name: string]: number };
  };
  time_shift: string;
};

// Define color mapping for concerns
const concernColors: { [concern: string]: string } = {
  Stress: "#ffadad",
  Depression: "#fdffb6",
  "Bipolar disorder": "#caffbf",
  Anxiety: "#9bf6ff",
  PTSD: "#ffd6a5",
  Insomnia: "#a0c4ff",
  ADHD: "#ffc6ff",
};

const Page = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [combinedAnalysis, setCombinedAnalysis] = useState<{
    timeline: {
      polarity: string;
      concerns: { name: string; intensity: number }[];
    }[];
  }>({ timeline: [] });

  useEffect(() => {
    const fetchSessions = async () => {
      const response = await fetch("http://localhost:8000/api/session/summary");
      const data: Session[] = await response.json();
      setSessions(data);
      console.log(data);

      const timelineData = data.flatMap((session) => ({
        polarity: session.metrics.polarity,
        concerns: session.metrics.concerns
          ? Object.entries(session.metrics.concerns)
              .filter(([, intensity]) => intensity > 0)
              .map(([name, intensity]) => ({ name, intensity }))
          : [],
      }));

      setCombinedAnalysis({ timeline: timelineData });
    };

    fetchSessions();
  }, []);

  const [overallTimeShift, setOverallTimeShift] = useState<string>("");
  useEffect(() => {
    const fetchOverallTimeShift = async () => {
      const response = await fetch(
        "http://localhost:8000/api/session/overalltimeshift"
      );
      const data = await response.json();
      setOverallTimeShift(data.time_shift);
    };

    fetchOverallTimeShift();
  }, []);

  if (sessions.length === 0) {
    return <div>Loading...</div>;
  }

  // Prepare data for Line Chart with color-coded concerns
  const chartData = {
    // labels: combinedAnalysis.timeline.map(item => item.date),
    labels: combinedAnalysis.timeline.map((_, index) => `Session ${index}`),
    datasets: [
      {
        label: "Polarity",
        data: combinedAnalysis.timeline.map((item) =>
          item.polarity === "positive"
            ? 1
            : item.polarity === "negative"
            ? -1
            : 0
        ),
        fill: false,
        borderColor: "rgba(75,192,192,1)",
        // tension: 0.1,
      },
      ...Array.from(
        new Set(
          combinedAnalysis.timeline.flatMap((item) =>
            item.concerns.map((c) => c.name)
          )
        )
      ).map((concern) => ({
        label: concern,
        data: combinedAnalysis.timeline.map((item) => {
          const concernObj = item.concerns.find((c) => c.name === concern);
          return concernObj ? concernObj.intensity : 0;
        }),
        fill: false,
        borderColor: concernColors[concern] || "#000000",
        tension: 0.1,
      })),
    ],
  };

  return (
    <div className="flex h-screen">
      {/* Left Side - Session View Tabs */}
      <div className="w-1/2 p-8 border-r overflow-y-scroll no-scrollbar scrollbar-none">
        <Tabs defaultValue={`session-0`}>
          <TabsList>
            {sessions.map((_, index) => (
              <TabsTrigger key={index} value={`session-${index}`}>
                {`Session ${index}`}
              </TabsTrigger>
            ))}
          </TabsList>
          {sessions.map((session, index) => (
            <TabsContent key={index} value={`session-${index}`}>
              <Card className="m-4">
                <CardHeader>
                  <CardTitle>Session Details</CardTitle>
                  <p className="text-sm text-gray-500">
                    {new Date(session.start_time).toLocaleString()}
                  </p>
                </CardHeader>
                <CardContent>
                  {session.messages.map((msg, idx) => (
                    <div key={idx} className="my-4 border-b pb-4">
                      <h3 className="text-lg font-bold">Message {idx + 1}</h3>
                      <p className="text-sm my-2">
                        <strong>Question:</strong> {msg.question}{" "}
                      </p>
                      <p className="text-sm my-2">
                        <strong>Response:</strong> {msg.response}
                      </p>
                      <p>{index == 0}</p>
                      {index != 0 && (
                        <div>
                          <p className="text-sm my-2">
                            <strong>Polarity:</strong> {msg.metrics.polarity}
                          </p>
                          <p className="text-sm my-2">
                            <strong>Key Phrase:</strong>{" "}
                            {msg.metrics.keywords.join(", ")}
                          </p>
                          <p className="text-sm my-2">
                            <strong>Concerns:</strong>
                          </p>
                          <ul>
                            {Object.entries(msg.metrics.concerns)
                              .filter(([, intensity]) => intensity > 0)
                              .map(([concern, intensity], j) => (
                                <li
                                  key={j}
                                  className="flex items-center gap-2 my-1"
                                >
                                  <span
                                    className="w-24"
                                    style={{ color: concernColors[concern] }}
                                  >
                                    {concern}
                                  </span>
                                  <Progress
                                    value={(intensity / 10) * 100}
                                    max={100}
                                    color={concernColors[concern]}
                                  />
                                  <span>{intensity}/10</span>
                                </li>
                              ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                  {/* Overall metrics */}
                  <div className="my-4 border-b pb-4">
                    <h3 className="text-lg font-bold">Overall Metrics</h3>
                    <p className="text-sm my-2">
                      <strong>Polarity:</strong> {session.metrics.polarity}
                    </p>
                    <p className="text-sm my-2">
                      <strong>Key Phrase:</strong>{" "}
                      {session.metrics?.keywords?.join(", ") ||
                        "No keywords available"}
                    </p>
                    <p className="text-sm my-2">
                      <strong>Concerns:</strong>
                    </p>
                    <ul>
                      {session.metrics?.concerns
                        ? Object.entries(session.metrics.concerns)
                            .filter(([, intensity]) => intensity > 0)
                            .map(([concern, intensity], j) => (
                              <li
                                key={j}
                                className="flex items-center gap-2 my-1"
                              >
                                <span
                                  className="w-24"
                                  style={{ color: concernColors[concern] }}
                                >
                                  {concern}
                                </span>
                                <Progress
                                  value={(intensity / 10) * 100}
                                  max={100}
                                  color={concernColors[concern]}
                                />
                                <span>{intensity}/10</span>
                              </li>
                            ))
                            .concat(
                              Array.from(
                                {
                                  length:
                                    9 -
                                    Object.entries(session.metrics.concerns)
                                      .length,
                                },
                                (_, j) => (
                                  <li
                                    key={`placeholder-${j}`}
                                    className="flex items-center gap-2 my-1"
                                  >
                                    <span
                                      className="w-24"
                                      style={{ color: "#ccc" }}
                                    >
                                      Placeholder
                                    </span>
                                    <Progress
                                      value={0}
                                      max={100}
                                      color="#ccc"
                                    />
                                    <span>0/10</span>
                                  </li>
                                )
                              )
                            )
                        : Array.from({ length: 9 }, (_, j) => (
                            <li
                              key={`placeholder-${j}`}
                              className="flex items-center gap-2 my-1"
                            >
                              <span
                                className="w-24"
                                style={{ color: "#ccc" }}
                              >
                                Placeholder
                              </span>
                              <Progress value={0} max={100} color="#ccc" />
                              <span>0/10</span>
                            </li>
                          ))}
                    </ul>
                    <p className="text-sm my-2">
                      <strong>Keystrokes:</strong> {session.metrics.keystrokes}
                    </p>
                    <p className="text-sm my-2">
                      <strong>Backspaces:</strong> {session.metrics.backspaces}
                    </p>
                    <p className="text-sm my-2">
                      <strong>Typing Speed:</strong> {session.metrics.speed} WPM
                    </p>
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col text-left justify-normal">
                  <h3 className="text-lg font-semibold text-left">
                    Estimated Persona
                  </h3>
                  <p className="text-left">{session.final_persona}</p>
                  <p className="mt-4"></p>
                  <h3 className="text-lg font-semibold text-left">
                    Recommendations
                  </h3>
                  <p className="text-left">{session.recommendation}</p>
                  <p className="mt-4"></p>
                  <h3 className="text-lg font-semibold text-left">
                    Time Shift Analysis
                  </h3>
                  <p className="text-left">{session.time_shift}</p>
                </CardFooter>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>

      {/* Right Side - Timeline-Based Sentiment Shift Analysis */}
      <div className="w-1/2 p-8 overflow-y-auto">
        <Card>
          <CardHeader>
            <CardTitle>Timeline-Based Sentiment Shift Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <Line data={chartData} />
            <p className="py-10 mt-16">{overallTimeShift}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Page;