"use client";

interface Props {
  progress: number;
  message: string;
  status: "pending" | "running" | "done" | "error";
}

export default function ProgressBar({ progress, message, status }: Props) {
  const color =
    status === "done" ? "bg-green-500" :
    status === "error" ? "bg-red-500" : "bg-blue-500";

  return (
    <div className="space-y-1">
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-xs text-gray-500">{message}</p>
    </div>
  );
}
