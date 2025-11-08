import {
	BadgeCheck,
	BadgeSwissFranc,
	Ban,
	CircleAlert,
	CircleUser,
	createIcons,
	DollarSign,
	Fingerprint,
	HatGlasses,
	IdCard,
	Info,
	LogIn,
	Menu,
	Moon,
	Palette,
	RefreshCw,
	Sun,
	SunMoon,
	UserRoundCheck,
	X,
} from "lucide";

const runIcons = () => {
	createIcons({
		icons: {
			BadgeCheck,
			BadgeSwissFranc,
			Ban,
			CircleAlert,
			CircleUser,
			DollarSign,
			Fingerprint,
			HatGlasses,
			IdCard,
			Info,
			LogIn,
			Menu,
			Moon,
			Palette,
			RefreshCw,
			Sun,
			SunMoon,
			UserRoundCheck,
			X,
		},
	});
};

runIcons();

document.addEventListener("agora:icons:refresh", () => {
	runIcons();
});
