export default function Card({ title, subtitle, children }) {
  return (
    <section className="rounded-2xl border border-white/60 bg-white/90 p-6 shadow-card backdrop-blur-sm">
      <header className="mb-5">
        <h2 className="text-xl font-semibold text-brand-900">{title}</h2>
        {subtitle ? <p className="text-sm text-brand-700">{subtitle}</p> : null}
      </header>
      {children}
    </section>
  );
}
