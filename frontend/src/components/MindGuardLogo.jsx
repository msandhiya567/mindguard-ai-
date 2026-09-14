function MindGuardLogo({ size = 42 }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.3,
        background: "var(--teal)",
        display: "grid",
        placeItems: "center",
        flexShrink: 0,
        boxShadow: "0 6px 18px rgba(63, 108, 99, 0.15)",
      }}
    >
      <svg
        width={size * 0.55}
        height={size * 0.55}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M32 52C32 52 8 38 8 21C8 13 14 8 21 8C26 8 30 11 32 15C34 11 38 8 43 8C50 8 56 13 56 21C56 38 32 52 32 52Z"
          fill="white"
        />

        <path
          d="M18 29C22 25 26 25 32 29C38 25 42 25 46 29"
          stroke="var(--teal)"
          strokeWidth="3"
          strokeLinecap="round"
        />

        <path
          d="M25 37C28 39 36 39 39 37"
          stroke="var(--teal)"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

export default MindGuardLogo;