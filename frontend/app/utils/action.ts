"use server";

const sendResume = async (
  prevState: { success: boolean; error: string },
  formData: FormData,
) => {
  const resumeText = formData.get("resume-text") as string;
  try {
    const res = await fetch("http://localhost:8000/resume/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: resumeText }),
    });

    if (!res.ok) {
      return {
        success: false,
        error: "Failed to send message",
      };
    }

    return {
      success: true,
      error: "",
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Something went wrong",
    };
  }
};

export default sendResume;
