// app/api/connection-details/route.ts
// or pages/api/connection-details.ts

import { AccessToken } from 'livekit-server-sdk';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { player_name, room_config } = body;

    // Get environment variables
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;
    const wsUrl = process.env.LIVEKIT_URL;

    if (!apiKey || !apiSecret || !wsUrl) {
      throw new Error('Server misconfigured');
    }

    // Create a unique room name
    const roomName = `improv-${Date.now()}`;
    const participantName = player_name || 'Player';

    // Create access token
    const at = new AccessToken(apiKey, apiSecret, {
      identity: participantName,
      name: participantName,
      // IMPORTANT: Pass player name in metadata
      metadata: JSON.stringify({ playerName: participantName }),
    });

    at.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
    });

    const token = await at.toJwt();

    return NextResponse.json({
      serverUrl: wsUrl,
      participantToken: token,
      participantName: participantName,
    });
  } catch (error) {
    console.error('Error creating connection details:', error);
    return NextResponse.json(
      { error: 'Failed to create connection details' },
      { status: 500 }
    );
  }
}