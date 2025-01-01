import { useEffect, useState, useCallback } from "react";
import localforage from "localforage";
import dayjs from "dayjs";
import siteConfig from "@/config/siteConfig";

const GITHUB_CACHE_HOURS = 2;

const fetchReleases = async () => {
  const gitResponse = await fetch(
    `https://api.github.com/repos/${siteConfig.repoOwner}/${siteConfig.repoName}/releases`
  );
  if (!gitResponse.ok) throw new Error(gitResponse.statusText);

  let newReleases = await gitResponse.json();

  if (!newReleases.length) throw new Error("No releases found");

  return newReleases;
};

export const useGithubReleases = () => {
  const [releasesStore, setReleasesStore] = useState({
    lastUpdate: null,
    releases: [],
  });

  const loadReleases = useCallback(async ({ forceUpdate = false } = {}) => {
    const storedStore = await localforage.getItem("releases");

    if (
      !forceUpdate &&
      storedStore &&
      dayjs().diff(dayjs(storedStore.lastUpdate), "hours") < GITHUB_CACHE_HOURS
    ) {
      return setReleasesStore(storedStore);
    }

      try {
        let newReleases = await fetchReleases();

        newReleases = newReleases.map((newRelease) => ({
          id: newRelease.id,
          html_url: newRelease.html_url,
          name: newRelease.name,
          published_at: newRelease.published_at,
          body: newRelease.body,
          avatar_url: newRelease.author.avatar_url,
          unread:
            storedStore?.releases.find(
              (storedRelease) => storedRelease.id === newRelease.id
            )?.unread ?? true,
        }));

      const updatedStore = {
        lastUpdate: dayjs().format(),
        releases: newReleases.slice(0, 6),
      };
      
      setReleasesStore(updatedStore);
      localforage.setItem("releases", updatedStore);
    } catch (error) {
      if (storedStore !== null) {
        return setReleasesStore(storedStore);
      }
    }
  }, []);

  useEffect(() => {
    loadReleases();
  }, [loadReleases]);

  const markAsRead = () => {
    const updatedStore = {
      ...releasesStore,
      releases: releasesStore.releases.map((release) => ({
        ...release,
        unread: false,
      })),
    };
    setReleasesStore(updatedStore);
    localforage.setItem("releases", updatedStore);
  };

  const forceUpdate = () => {
    loadReleases({ forceUpdate: true });
  }

  return {
    releases: releasesStore.releases,
    lastUpdate: releasesStore.lastUpdate,
    unreadCount: releasesStore.releases.reduce(
      (count, release) => (release.unread ? count + 1 : count),
      0
    ),
    markAsRead,
    forceUpdate,
  };
}; 