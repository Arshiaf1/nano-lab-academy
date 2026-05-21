"use client";

type Props = {
  src?: string;
  poster?: string;
  title?: string;
};

export function VideoPlayer({
  src = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
  poster,
  title,
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-black">
      <video
        className="h-auto w-full"
        controls
        playsInline
        poster={poster}
        src={src}
      >
        {title ? `${title} video` : "Video playback is not supported."}
      </video>
    </div>
  );
}
