export default function Layout({ children }) {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-5xl">{children}</div>
    </main>
  );
}
