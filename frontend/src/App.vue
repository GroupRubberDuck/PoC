<template>
  <div class="app-container">
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background-color: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.navbar-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
}

.logo {
  font-size: 1.8rem;
}

.main-content {
  flex-grow: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>