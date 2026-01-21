import NextAuth from 'next-auth'
import Credentials from 'next-auth/providers/credentials'
import Google from 'next-auth/providers/google'
import Kakao from 'next-auth/providers/kakao'
import { login as backendLogin } from '@/lib/api/auth.api'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        try {
          if (!credentials?.email || !credentials?.password) {
            return null
          }

          // Call backend login API
          const result = await backendLogin({
            email: credentials.email as string,
            password: credentials.password as string,
          })

          // Return user object (will be stored in JWT)
          return {
            id: credentials.email as string,
            email: credentials.email as string,
            accessToken: result.accessToken,
            refreshToken: result.refreshToken,
          }
        } catch (error) {
          console.error('Credentials authorize error:', error)
          return null
        }
      },
    }),
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET,
    }),
    Kakao({
      clientId: process.env.AUTH_KAKAO_ID,
      clientSecret: process.env.AUTH_KAKAO_SECRET,
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Initial sign in
      if (user) {
        token.accessToken = user.accessToken
        token.refreshToken = user.refreshToken
      }
      return token
    },
    async session({ session, token }) {
      return {
        ...session,
        accessToken: token.accessToken,
      }
    },
  },
  pages: {
    signIn: '/auth/login',
    error: '/auth/login',
  },
})
