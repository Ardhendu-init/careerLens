import Header from "@/app/components/Header";
import LoginForm from "./LoginForm";

export default function LoginPage() {
  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-sm flex-1 px-6 py-10">
        <h2 className="mb-6 text-center text-2xl font-bold tracking-tight">
          Log in
        </h2>
        <LoginForm />
      </main>
    </>
  );
}
