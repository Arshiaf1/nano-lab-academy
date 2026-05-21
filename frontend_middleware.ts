import { NextRequest, NextResponse } from 'next/server';

const publicRoutes = ['/auth/login', '/auth/register', '/'];
const protectedRoutes = ['/(protected)'];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get('token')?.value;

  // Check if the route is public
  const isPublicRoute = publicRoutes.includes(pathname);

  if (!token && !isPublicRoute) {
    // Redirect to login if no token and route is protected
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  if (token && (pathname === '/auth/login' || pathname === '/auth/register')) {
    // Redirect to dashboard if already logged in and trying to access auth pages
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|public).*)'],
};
