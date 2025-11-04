import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { setUser } from '@/lib/slices/user'
import { useNavigate } from 'react-router'

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from '@/components/ui/input'

import { api } from '@/lib/api'

export default function login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loginOrSignup, setLoginOrSignup] = useState<'login' | 'signup'>('login')

  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleSubmit = async () => {
    const endpoint = loginOrSignup === 'login' ? '/user/login' : '/user/signup'
    try {
      const res = await api(endpoint, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (res.ok) {
        console.log(data);
        dispatch(setUser({ username, user_id: data.user_id, store_id: data.store_id }));
        navigate('/');
      } else {
        setError(`❌ ${data.message || 'เกิดข้อผิดพลาดบางอย่าง'}`);
      }
    } catch (err) {
      setError(`❌ เกิดข้อผิดพลาดบางอย่าง: ${err}`);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{loginOrSignup === 'login' ? 'Login' : 'Sign Up'}</CardTitle>
          <CardDescription>
            กรุณาใส่ Username และ Password เพื่อเข้าสู่ระบบ
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form>
            <FieldGroup className="flex flex-col gap-2 mb-4">
              <FieldLabel>Username</FieldLabel>
              <Input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="ใส่ Username"
                required
              />
            </FieldGroup>
            <FieldGroup className="flex flex-col gap-2 mb-4">
              <FieldLabel>Password</FieldLabel>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="ใส่ Password"
                required
              />
            </FieldGroup>
          </form>
          {/* <Input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mb-4"
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          /> */}
        </CardContent>
        <CardFooter className='flex flex-col gap-2 items-start'>
          <div className='flex flex-row gap-2'>
            <Button className="w-full" onClick={handleSubmit}>
              {loginOrSignup === 'login' ? 'Login' : 'Sign Up'}
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setLoginOrSignup(loginOrSignup === 'login' ? 'signup' : 'login')}
            >
              Switch to {loginOrSignup === 'login' ? 'Sign Up' : 'Login'}
            </Button>
          </div>
          {error && <p className="text-destructive mt-2">{error}</p>}
        </CardFooter>
      </Card>
    </>
  )
}
