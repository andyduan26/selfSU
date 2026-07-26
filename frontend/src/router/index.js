import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import CourseCategoryView from '../views/CourseCategoryView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import LoginView from '../views/LoginView.vue'
import LessonPlayView from '../views/LessonPlayView.vue'
import ProfileView from '../views/ProfileView.vue'
import RegisterView from '../views/RegisterView.vue'
import TeacherApplicationView from '../views/TeacherApplicationView.vue'
import TeacherCenterView from '../views/TeacherCenterView.vue'
import TeacherPublicView from '../views/TeacherPublicView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/courses',
      name: 'course-category',
      component: CourseCategoryView,
    },
    {
      path: '/courses/:id',
      name: 'course-detail',
      component: CourseDetailView,
    },
    {
      path: '/teachers/:id',
      name: 'teacher-public',
      component: TeacherPublicView,
    },
    {
      path: '/lessons/:id/play',
      name: 'lesson-play',
      component: LessonPlayView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/teacher/apply',
      name: 'teacher-apply',
      component: TeacherApplicationView,
      meta: { requiresAuth: true },
    },
    {
      path: '/teacher',
      name: 'teacher-center',
      component: TeacherCenterView,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }
  if ((to.name === 'login' || to.name === 'register') && authStore.isAuthenticated) {
    return { name: 'profile' }
  }
  return true
})

export default router
