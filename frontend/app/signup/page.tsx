import Header from "@/app/components/Header";
import SignupForm from "./SignupForm";

export default function SignupPage() {
  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-sm flex-1 px-6 py-10">
        <h2 className="mb-6 text-center text-2xl font-bold tracking-tight">
          Sign up
        </h2>
        <SignupForm />
      </main>
    </>
  );
}
