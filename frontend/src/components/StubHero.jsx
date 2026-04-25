export default function StubHero({ icon, title, subtitle }) {
  return (
    <div className="stub-hero">
      <div className="stub-hero-icon">{icon}</div>
      <div className="stub-hero-content">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
    </div>
  );
}
