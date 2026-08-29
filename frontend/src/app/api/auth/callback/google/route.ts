import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const error = searchParams.get('error');

  const redirectUrl = new URL('/auth/callback/google', request.url);
  if (code) redirectUrl.searchParams.set('code', code);
  if (error) redirectUrl.searchParams.set('error', error);

  return NextResponse.redirect(redirectUrl);
}
