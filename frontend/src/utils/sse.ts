export interface SSECallbacks<T = unknown> {
  onEvent: (event: string, data: T) => void;
}

export async function parseSSE(
  response: Response,
  callbacks: SSECallbacks
) {
  if (!response.body) {
    throw new Error("Streaming not supported.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, {
      stream: true,
    });

    const events = buffer.split("\n\n");

    buffer = events.pop() ?? "";

    for (const eventBlock of events) {
      const lines = eventBlock.split("\n");

      let event = "";
      let data = "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          event = line.substring(6).trim();
        }

        if (line.startsWith("data:")) {
          data = line.substring(5).trim();
        }
      }

      if (!event || !data) continue;

      callbacks.onEvent(
        event,
        JSON.parse(data)
      );
    }
  }
}