import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { AuthStore } from "./auth.svelte";

// Mock the API module
vi.mock("$lib/api", () => ({
  getCurrentUser: vi.fn(),
  refreshToken: vi.fn(),
}));

import { getCurrentUser, refreshToken } from "$lib/api";

describe("AuthStore", () => {
  let authStore: AuthStore;
  let localStorageMock: { [key: string]: string };

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Mock localStorage
    localStorageMock = {};
    vi.stubGlobal("localStorage", {
      getItem: vi.fn((key: string) => localStorageMock[key] || null),
      setItem: vi.fn((key: string, value: string) => {
        localStorageMock[key] = value;
      }),
      removeItem: vi.fn((key: string) => {
        delete localStorageMock[key];
      }),
    });

    // Create fresh store
    authStore = new AuthStore();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("initial state", () => {
    it("should start with null token and user", () => {
      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();
      expect(authStore.isLoading).toBe(false);
      expect(authStore.isInitialized).toBe(false);
    });

    it("should restore token from localStorage", () => {
      localStorageMock["access_token"] = "stored-token";
      const store = new AuthStore();
      expect(store.token).toBe("stored-token");
    });
  });

  describe("isAuthenticated", () => {
    it("should be false when no token", () => {
      expect(authStore.isAuthenticated).toBe(false);
    });

    it("should be true when token is set and not loading", () => {
      authStore.setToken("test-token");
      expect(authStore.isAuthenticated).toBe(true);
    });

    it("should be false when loading", () => {
      authStore.setToken("test-token");
      authStore.isLoading = true;
      expect(authStore.isAuthenticated).toBe(false);
    });
  });

  describe("setToken", () => {
    it("should set token and persist to localStorage", () => {
      authStore.setToken("new-token");
      expect(authStore.token).toBe("new-token");
      expect(localStorage.setItem).toHaveBeenCalledWith(
        "access_token",
        "new-token",
      );
    });
  });

  describe("setUser", () => {
    it("should set user", () => {
      const user = {
        id: 1,
        email: "test@example.com",
        name: "Test User",
        student_id: null,
        is_active: true,
        is_admin: false,
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      };
      authStore.setUser(user);
      expect(authStore.user).toEqual(user);
    });
  });

  describe("logout", () => {
    it("should clear token, user, and localStorage", () => {
      authStore.setToken("test-token");
      authStore.setUser({
        id: 1,
        email: "test@example.com",
        name: "Test",
        student_id: null,
        is_active: true,
        is_admin: false,
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      });

      authStore.logout();

      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();
      expect(localStorage.removeItem).toHaveBeenCalledWith("access_token");
    });
  });

  describe("getAuthHeaders", () => {
    it("should return empty object when no token", () => {
      expect(authStore.getAuthHeaders()).toEqual({});
    });

    it("should return Authorization header when token exists", () => {
      authStore.setToken("my-token");
      expect(authStore.getAuthHeaders()).toEqual({
        Authorization: "Bearer my-token",
      });
    });
  });

  describe("initialize", () => {
    const mockUser = {
      id: 1,
      email: "test@example.com",
      name: "Test User",
      student_id: null,
      is_active: true,
      is_admin: false,
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
    };

    it("should mark as initialized immediately if no token", async () => {
      await authStore.initialize();
      expect(authStore.isInitialized).toBe(true);
      expect(getCurrentUser).not.toHaveBeenCalled();
    });

    it("should fetch user when token exists", async () => {
      authStore.setToken("valid-token");
      vi.mocked(getCurrentUser).mockResolvedValueOnce(mockUser);

      await authStore.initialize();

      expect(getCurrentUser).toHaveBeenCalledWith("valid-token");
      expect(authStore.user).toEqual(mockUser);
      expect(authStore.isInitialized).toBe(true);
      expect(authStore.isLoading).toBe(false);
    });

    it("should try refresh token on getCurrentUser failure", async () => {
      authStore.setToken("expired-token");
      vi.mocked(getCurrentUser)
        .mockRejectedValueOnce(new Error("Unauthorized"))
        .mockResolvedValueOnce(mockUser);
      vi.mocked(refreshToken).mockResolvedValueOnce({
        access_token: "new-token",
        token_type: "bearer",
      });

      await authStore.initialize();

      expect(refreshToken).toHaveBeenCalledWith("expired-token");
      expect(authStore.token).toBe("new-token");
      expect(authStore.user).toEqual(mockUser);
    });

    it("should logout when refresh also fails", async () => {
      authStore.setToken("invalid-token");
      vi.mocked(getCurrentUser).mockRejectedValueOnce(
        new Error("Unauthorized"),
      );
      vi.mocked(refreshToken).mockRejectedValueOnce(
        new Error("Refresh failed"),
      );

      await authStore.initialize();

      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();
      expect(authStore.isInitialized).toBe(true);
    });

    it("should only initialize once", async () => {
      authStore.setToken("valid-token");
      vi.mocked(getCurrentUser).mockResolvedValue(mockUser);

      await authStore.initialize();
      await authStore.initialize();

      expect(getCurrentUser).toHaveBeenCalledTimes(1);
    });
  });

  describe("handleUnauthorized", () => {
    const mockUser = {
      id: 1,
      email: "test@example.com",
      name: "Test User",
      student_id: null,
      is_active: true,
      is_admin: false,
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
    };

    it("should return true and refresh on success", async () => {
      authStore.setToken("old-token");
      vi.mocked(refreshToken).mockResolvedValueOnce({
        access_token: "refreshed-token",
        token_type: "bearer",
      });
      vi.mocked(getCurrentUser).mockResolvedValueOnce(mockUser);

      const result = await authStore.handleUnauthorized();

      expect(result).toBe(true);
      expect(authStore.token).toBe("refreshed-token");
      expect(authStore.user).toEqual(mockUser);
    });

    it("should return false and logout on failure", async () => {
      authStore.setToken("expired-token");
      vi.mocked(refreshToken).mockRejectedValueOnce(new Error("Failed"));

      const result = await authStore.handleUnauthorized();

      expect(result).toBe(false);
      expect(authStore.token).toBeNull();
      expect(authStore.user).toBeNull();
    });
  });
});
