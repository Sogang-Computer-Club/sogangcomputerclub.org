import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { GOOGLE_API_KEY, CALENDAR_ID } from '$env/static/private';

/**
 * Server-side proxy for Google Calendar API.
 * Keeps the API key secure on the server.
 */
export const GET: RequestHandler = async ({ fetch }) => {
    if (!GOOGLE_API_KEY || !CALENDAR_ID) {
        return json(
            { error: 'Calendar configuration missing' },
            { status: 500 }
        );
    }

    const url = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CALENDAR_ID)}/events?key=${GOOGLE_API_KEY}&singleEvents=true&orderBy=startTime`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            console.error('Google Calendar API error:', response.status, response.statusText);
            return json(
                { error: 'Failed to fetch calendar events' },
                { status: response.status }
            );
        }

        const data = await response.json();

        // Return only the necessary fields to minimize data exposure
        const events = (data.items || []).map((event: any) => ({
            summary: event.summary,
            start: event.start,
            end: event.end,
            location: event.location,
            description: event.description
        }));

        return json({ items: events });
    } catch (error) {
        console.error('Error fetching calendar data:', error);
        return json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
};
