import Ripple from "@/components/ui/ripple";

export default function Home() {
  return (
    <>
    <div className="relative flex  min-h-screen w-full flex-col items-center justify-center rounded-lg border bg-background md:shadow-xl">
      <p className="z-10 whitespace-pre-wrap text-center text-5xl font-medium tracking-tighter text-white">
        PeerTalk
      </p>
      <Ripple />
    </div>

    </>
  );
}
