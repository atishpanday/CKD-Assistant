"use client";
import ReactMarkdown from 'react-markdown';
import { useState } from "react";

type Message = {
    id: string,
    role: string,
    content: string,
};

export const initialMessages: Message[] = [
    {
        role: "assistant",
        id: "0",
        content: "Hi! I am your clinical AI assistant. What can I help you with today?",
    },
];

async function* getMessageResponse(messages: Message[]) {
    const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(messages),
    });
    if (!response.body) {
        return "No response received";
    }

    const textDecoder = new TextDecoder("utf-8");
    const reader = response.body?.getReader();

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            break;
        }

        yield* textDecoder.decode(value, { stream: true });
    }
};

function Chat() {
    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [input, setInput] = useState<string>("");

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        const userMessage: Message = {
            id: messages.length.toString(),
            role: "user",
            content: input,
        }
        setMessages(prev => [...prev, {
            id: prev.length.toString(),
            role: "user",
            content: input
        }]);
        setInput("");
        const currMessages = [...messages, userMessage];
        const aiMessageId = (messages.length + 1).toString();
        setMessages((prev) => [
            ...prev,
            {
                id: aiMessageId,
                role: "assistant",
                content: "",
            },
        ]);

        let aiMessageContent = "";
        for await (const chunk of getMessageResponse(currMessages)) {
            aiMessageContent += chunk
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === aiMessageId
                        ? { ...msg, content: aiMessageContent }
                        : msg
                )
            );
        }
    };

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        setInput(e.currentTarget.value);
    };

    return (
        <div className="max-w-2xl mx-auto p-4">
            {messages.map((m) => (
                <div key={m.id} className="mb-4">
                    <div className={`rounded-lg p-3 ${m.role === "user" ? "bg-blue-100 text-blue-900" : "bg-gray-100 text-gray-900"} shadow-md`}>
                        <ReactMarkdown>
                            {`${m.role === "user" ? "User: " : "AI: "} ${m.content}`}
                        </ReactMarkdown>
                    </div>
                </div>
            ))}
            <form onSubmit={handleSubmit} className="mt-4">
                <input
                    className="w-full rounded-lg border border-gray-300 shadow-sm px-4 py-2 focus:outline-none focus:border-blue-500"
                    value={input}
                    placeholder="Say something..."
                    onChange={handleInputChange}
                />
            </form>
        </div>
    );
};

export default Chat;