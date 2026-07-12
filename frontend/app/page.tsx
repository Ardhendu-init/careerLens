import Header from "@/app/components/Header";
import ResumeForm from "@/app/components/ResumeForm";
import ResumeWorkspace from "@/app/components/ResumeWorkspace";
import { getMyResumes } from "@/app/lib/resumes";

export default async function Home() {
  const resumes = await getMyResumes();

  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-10">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">
            See how you stack up
          </h2>
          <p className="mx-auto mt-2 max-w-xl text-sm text-muted">
            Save your resume once, then analyze it against any job description
            to get a match score, the skills you have, the ones you&apos;re
            missing, and advice on how to position yourself.
          </p>
        </div>

        <div className="space-y-6">
          {resumes.length === 0 ? (
            <ResumeForm />
          ) : (
            <ResumeWorkspace resumes={resumes} />
          )}
        </div>
      </main>

      <footer className="border-t border-border py-6 text-center text-xs text-muted">
        CareerLens · resume-to-JD matching
      </footer>
    </>
  );
}
