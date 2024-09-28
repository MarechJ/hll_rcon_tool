import Image from 'next/image';

export default function MapFigure({ src, name, text, muted } : { src: string, name: string, text?: string, muted?: boolean }) {
  return (
    <figure className="relative w-1/2 h-10 xl:h-full">
      <Image
        src={src}
        alt=""
        fill
        style={{ objectFit: 'cover' }}
        className={muted ? "grayscale-[50]" : ""}
      />
      <figcaption className="absolute bottom-0 w-full p-1 text-center text-sm font-bold bg-background/75">
        {text && <div className="text-xs">{text}</div>}
        <div>{name}</div>
      </figcaption>
    </figure>
  );
}
