import {
    get,
    execute,
  } from "@/utils/fetchUtils";
  import {  toast } from "react-toastify";
  import { defer } from "react-router-dom";
import PlayerProfilePage from './index';
import PlayerDetailView from './[detail]';

const fetchResource = async (url, errorMessage) => {
    try {
      const response = await get(url);
      if (!response.ok) throw new Response(errorMessage, { status: 404 });
      const data = await response.json();
      if (!data.result) throw new Response(errorMessage, { status: 404 });
      return data.result;
    } catch (error) {
      console.warn(`Failed to fetch ${url}:`, error);
      return null; // Return null if any request fails
    }
  };
  
  export const loader = async ({ params, request }) => {
    const { playerId } = params;
    const url = new URL(request.url);
    const numSessions = url.searchParams.get('num_sessions') || 10;
  
    // Use the fetchResource function for each API call
    const fetchPlayer = fetchResource(
      `get_player_profile?player_id=${playerId}&num_sessions=${numSessions}`,
      "Player not found"
    );
  
    const fetchMessages = fetchResource(
      `get_player_messages?player_id=${playerId}`,
      "Messages not found"
    );
  
    // Run all promises concurrently
    const [profile, messages] = await Promise.all([
      fetchPlayer,
      fetchMessages,
    ]);
  
    // If player is not found, throw an error
    if (!profile) {
      throw new Response("Player not found", { status: 404 });
    }
  
    // Return a deferred object to allow data to load in parallel
    return defer({
      profile,
      messages,
      numSessions,
    });
  };
  
  export const action = async ({ request }) => {
    let formData = await request.formData();
    const url = new URL(request.url);
    const currentPath = url.pathname.split('/').pop();
  
    try {
      const res = await execute(
        'post_player_comment',
        {
          player_id: formData.get("player_id"),
          comment: formData.get("comment"),
        }
      );
      if (!res.ok) throw res;
      
      // Return success and maintain current path
      return { ok: true, currentPath };
    } catch (error) {
      toast.error('Failed to save the comment.')
      return { ok: false, error }
    }
  };

export const route = {
  element: <PlayerProfilePage />,
  loader,
  action,
  children: [
    {
      index: true,
      loader: ({ request }) => {
        const url = new URL(request.url);
        const currentPath = url.pathname.split('/').pop();
        // If we're coming back from an action, maintain the path
        if (currentPath && currentPath !== 'players') {
          return defer({ redirect: currentPath });
        }
        return defer({ redirect: 'sessions' });
      },
    },
    {
      path: 'sessions',
      element: <PlayerDetailView />,
    },
    {
      path: 'activities',
      element: <PlayerDetailView />,
    },
    {
      path: 'names',
      element: <PlayerDetailView />,
    },
    {
      path: 'comments',
      element: <PlayerDetailView />,
    },
    {
      path: 'logs',
      element: <PlayerDetailView />,
    },
  ],
};