"use client"; // Entire page as client component for simplicity (can optimize later)
import { useState } from "react";
import axios, { AxiosError } from "axios";
import { FaPaperPlane } from "react-icons/fa";
import TestDiv from "../components/TestDiv";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface FormData {
  user_id: string;
  age: number;
  weight: number;
  height: string;
  gender: string;
  preferences: string;
  restrictions: string;
  goal: string;
}

export default function Home() {
  const [formData, setFormData] = useState<FormData>({
    user_id: "",
    age: 0,
    weight: 0,
    height: "",
    gender: "",
    preferences: "",
    restrictions: "",
    goal: "",
  });
  const [userQuery, setUserQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isFormOpen, setIsFormOpen] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const formDataToSend = new FormData();
      formDataToSend.append("user_id", formData.user_id);
      formDataToSend.append("age", String(formData.age));
      formDataToSend.append("weight", String(formData.weight));
      formDataToSend.append("height", formData.height);
      formDataToSend.append("gender", formData.gender);
      formDataToSend.append("preferences", formData.preferences);
      formDataToSend.append("restrictions", formData.restrictions);
      formDataToSend.append("goal", formData.goal);

      await axios.post(`${API_URL}/submit-details/`, formDataToSend, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: "Profile saved successfully." },
      ]);
      setIsFormOpen(false);
    } catch (error) {
      const axiosError = error as AxiosError;
      setError("Failed to save profile. Please try again.");
      console.error(
        "Error submitting profile:",
        axiosError.response?.data || axiosError
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!userQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.post(
        `${API_URL}/chat/`,
        { user_id: formData.user_id, query: userQuery },
        { headers: { "Content-Type": "application/json" } }
      );
      console.log("Chat response received:", response.data);
      setChatHistory((prev) => [
        ...prev,
        { role: "user", content: userQuery },
        { role: "assistant", content: response.data.response },
      ]);
      setUserQuery("");
    } catch (error) {
      const axiosError = error as AxiosError;
      setError("Failed to get response. Please try again.");
      console.error(
        "Error chatting:",
        axiosError.response?.data || axiosError
      );
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Content copied to clipboard!");
  };

  return (
    <>
      <TestDiv />
      <div className="min-h-screen bg-gradient-to-br from-emerald-900 to-gray-900 text-gray-200 font-inter flex">
      <aside className="w-80 p-4 space-y-4 bg-gray-800 bg-opacity-90 shadow-lg">
          <h1 className="text-xl font-bold text-gray-100">Profile</h1>
          <button
            onClick={() => setIsFormOpen(!isFormOpen)}
            className="w-full text-left text-emerald-400 hover:text-emerald-300"
          >
            {isFormOpen ? "Hide Form" : "Show Form"}
          </button>
          {isFormOpen && (
            <div className="space-y-4">
              <form onSubmit={handleSubmit} className="space-y-2">
                <input
                  type="text"
                  placeholder="Enter the User ID"
                  value={formData.user_id}
                  onChange={(e) =>
                    setFormData({ ...formData, user_id: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                />
                <input
                  type="number"
                  placeholder="Enter your Age"
                  value={formData.age}
                  onChange={(e) =>
                    setFormData({ ...formData, age: Number(e.target.value) })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                />
                <input
                  type="number"
                  placeholder="Enter your Weight (kg)"
                  value={formData.weight}
                  onChange={(e) =>
                    setFormData({ ...formData, weight: Number(e.target.value) })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                />
                <input
                  type="text"
                  placeholder="Enter your Height (Eg. 180 cm)"
                  value={formData.height}
                  onChange={(e) =>
                    setFormData({ ...formData, height: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                />
                <select
                  value={formData.gender}
                  onChange={(e) =>
                    setFormData({ ...formData, gender: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                >
                  <option value="">Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
                <input
                  type="text"
                  placeholder="Preferences (e.g., vegetarian)"
                  value={formData.preferences}
                  onChange={(e) =>
                    setFormData({ ...formData, preferences: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
                <input
                  type="text"
                  placeholder="Restrictions"
                  value={formData.restrictions}
                  onChange={(e) =>
                    setFormData({ ...formData, restrictions: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
                <select
                  value={formData.goal}
                  onChange={(e) =>
                    setFormData({ ...formData, goal: e.target.value })
                  }
                  className="w-full p-2 border border-gray-700 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required
                >
                  <option value="">Goal</option>
                  <option value="muscle_gain">Muscle Gain</option>
                  <option value="weight_loss">Weight Loss</option>
                  <option value="maintenance">Maintenance</option>
                </select>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-emerald-600 text-white p-2 rounded-md hover:bg-emerald-700 transition-colors disabled:bg-emerald-400"
                >
                  {loading ? "Saving..." : "Save"}
                </button>
              </form>
              {error && <p className="text-red-400 text-sm">{error}</p>}
            </div>
          )}
        </aside>
        <main className="flex-1 p-4 flex flex-col items-center">
          <div className="w-full max-w-6xl bg-gray-800 bg-opacity-90 rounded-lg shadow-lg p-6 space-y-4">
            <h1 className="text-lg font-bold text-gray-100">
              How can I assist you?
            </h1>
            {chatHistory.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                } animate-fade-in`}
              >
                <div
                  className={`max-w-prose p-3 rounded-lg shadow-md ${
                    msg.role === "user"
                      ? "bg-emerald-600 text-white"
                      : "bg-gray-700 text-gray-200"
                  }`}
                >
                  {msg.role === "assistant" && msg.content.startsWith("### Meal Plan") ? (
                    <div>
                      <h3 className="text-md font-bold mb-2">Meal Plan</h3>
                      <p className="mb-2">
                        {
                          msg.content
                            .split("\n")
                            .find((line) =>
                              line.startsWith("**Recommended daily calories**")
                            )!
                        }
                      </p>
                      <div className="space-y-2">
                        {msg.content
                          .split("\n")
                          .filter((line) => line.match(/^\d\./))
                          .map((meal, i) => (
                            <div
                              key={i}
                              className="bg-gray-600 p-2 rounded-md border border-gray-500 hover:bg-gray-500 transition-transform hover:scale-[1.02]"
                            >
                              <p className="text-sm">{meal}</p>
                            </div>
                          ))}
                      </div>
                      <button
                        onClick={() => copyToClipboard(msg.content)}
                        className="mt-2 text-sm text-emerald-400 hover:underline"
                      >
                        Copy Meal Plan
                      </button>
                    </div>
                  ) : msg.role === "assistant" && (msg.content.startsWith("### Recipe") || msg.content.startsWith("### Recipe Confirmation")) ? (
                    <div>
                      <h3 className="text-md font-bold mb-2">
                        {msg.content.split("\n")[0].replace("### ", "").trim()}
                      </h3>
                      <div className="space-y-2">
                        {msg.content
                          .split("\n\n")
                          .filter((section) => section.trim())
                          .map((section, i) => (
                            <p
                              key={i}
                              className="text-sm whitespace-pre-wrap"
                              style={{ margin: 0 }}
                            >
                              {section.trim()}
                            </p>
                          ))}
                      </div>
                      <button
                        onClick={() => copyToClipboard(msg.content)}
                        className="mt-2 text-sm text-emerald-400 hover:underline"
                      >
                        Copy Recipe
                      </button>
                    </div>
                  ) : msg.role === "assistant" && msg.content.startsWith("### Nutritional Content") ? (
                    <div>
                      <h3 className="text-md font-medium mb-2">
                        {msg.content.split("\n")[0].replace("### Nutritional Content of ", "").trim()}
                      </h3>
                      <div className="space-y-2">
                        {msg.content
                          .split("\n\n")
                          .filter((section) => section.trim())
                          .map((section, i) => (
                            <div
                              key={i}
                              dangerouslySetInnerHTML={{
                                __html: section
                                  .trim()
                                  .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
                                  .replace(/\*(.*?)\*/g, "<i>$1</i>"), // Optional: italicize single *
                              }}
                            />
                          ))}
                      </div>
                      <button
                        onClick={() => copyToClipboard(msg.content)}
                        className="mt-2 text-sm text-emerald-400 hover:underline"
                      >
                        Copy Nutritional Content
                      </button>
                    </div>
                  ) : (
                    <p className="text-sm">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={userQuery}
                onChange={(e) => setUserQuery(e.target.value)}
                placeholder="Enter your query"
                className="flex-1 p-2 border border-gray-600 rounded-md bg-gray-700 text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                onKeyPress={(e) => e.key === "Enter" && handleChat()}
              />
              <button
                onClick={handleChat}
                disabled={loading}
                className="bg-emerald-600 text-white p-2 rounded-md hover:bg-emerald-700 transition-colors disabled:bg-emerald-400"
              >
                <FaPaperPlane />
              </button>
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Note: AI may generate errors. Verify critical data.
          </p>
        </main>
      </div>
    </>
  );
}