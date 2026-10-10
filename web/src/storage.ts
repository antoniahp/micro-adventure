// There are no accounts: the browser creates an anonymous user id and remembers it. session.ts asks the server
// to accept it and keeps the tokens that prove it is this browser's.

export function getUserId(): string {
  let userId = localStorage.getItem("userId");
  if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem("userId", userId);
  }
  return userId;
}

export function setUserId(userId: string) {
  localStorage.setItem("userId", userId);
}

export function resetUserId() {
  localStorage.removeItem("userId");
  localStorage.removeItem("walkId"); // that walk belonged to the old id
}

export const currentWalk = {
  get: () => localStorage.getItem("walkId"),
  set: (walkId: string) => localStorage.setItem("walkId", walkId),
  clear: () => localStorage.removeItem("walkId"),
};
