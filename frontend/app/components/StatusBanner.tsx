type Status = "idle" | "success" | "error";

export default function StatusBanner({
  status,
  message,
}: {
  status: Status;
  message: string;
}) {
  if (status === "idle" || !message) return null;

  const isError = status === "error";

  return (
    <p
      aria-live="polite"
      className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${
        isError
          ? "border-danger/30 bg-danger/10 text-danger"
          : "border-success/30 bg-success/10 text-success"
      }`}
    >
      <span aria-hidden>{isError ? "⚠" : "✓"}</span>
      {message}
    </p>
  );
}
