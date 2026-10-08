// The app's mark: a compass whose needle spins and settles when the app opens,
// then gives a small shake now and then, like looking for the way.
export default function Logo({ size = 32 }: { size?: number }) {
  return (
    <svg className="logo" width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <circle cx="16" cy="16" r="16" fill="#25235F" />
      <circle cx="16" cy="16" r="12.5" fill="none" stroke="#fff" strokeOpacity="0.35" strokeWidth="1.5" />
      <g stroke="#fff" strokeOpacity="0.6" strokeWidth="1.5" strokeLinecap="round">
        <path d="M16 2.8v2.2M16 27v2.2M2.8 16H5M27 16h2.2" />
      </g>
      <g className="logo-needle">
        <path d="M16 6.5l3.2 9.5H12.8z" fill="#F25C54" />
        <path d="M16 25.5l-3.2-9.5h6.4z" fill="#FFB300" />
      </g>
      <circle cx="16" cy="16" r="1.8" fill="#fff" />
    </svg>
  );
}
