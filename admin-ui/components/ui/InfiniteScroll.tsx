"use client";

import { useEffect, useRef } from "react";

export function InfiniteScroll({
  disabled,
  loading,
  onLoadMore
}: {
  disabled: boolean;
  loading: boolean;
  onLoadMore: () => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node || disabled || loading) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          onLoadMore();
        }
      },
      { rootMargin: "320px 0px" }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [disabled, loading, onLoadMore]);

  return <div ref={ref} className="h-8 w-full" aria-hidden />;
}
