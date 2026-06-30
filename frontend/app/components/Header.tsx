export default function Header() {
  return (
    <header className="border-b border-border bg-card/60 backdrop-blur">
      <div className="mx-auto flex max-w-3xl items-center gap-3 px-6 py-4">
        <div className="flex size-9 items-center justify-center rounded-lg bg-brand text-brand-fg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="size-5"
            aria-hidden
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m21 21-4.3-4.3" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold leading-tight">CareerLens</h1>
          <p className="text-xs text-muted">
            Match your resume against any job description
          </p>
        </div>
      </div>
    </header>
  );
}
