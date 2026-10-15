import { setupServer } from "msw/node";

// the API at the network boundary; each test adds its own answers with server.use
export const server = setupServer();
