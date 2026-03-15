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
  const inFlightRef = useRef(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || disabled || loading) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const inView = Boolean(entries[0]?.isIntersecting);
        const hasMore = !disabled;
        if (inView && hasMore && !loading && !inFlightRef.current) {
          inFlightRef.current = true;
          onLoadMore();
          window.setTimeout(() => {
            inFlightRef.current = false;
          }, 300);
        }
      },
      { rootMargin: "320px 0px" }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [disabled, loading, onLoadMore]);

  return <div ref={ref} className="h-8 w-full" aria-hidden />;
}
