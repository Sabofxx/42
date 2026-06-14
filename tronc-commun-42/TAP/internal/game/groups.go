package game

import (
	"tap/internal/logging"
	"tap/internal/protocol"
)

// groupCreateLocked handles GROUP CREATE.
func (g *Game) groupCreateLocked(p *Player) string {
	if p.Group != "" {
		return protocol.Err(protocol.ErrAlreadyInGroup, "ALREADY_IN_GROUP")
	}
	g.nextGroup++
	id := "grp." + itoa(g.nextGroup)
	g.groups[id] = &group{id: id, members: map[string]bool{p.Name: true}}
	p.Group = id
	g.log.Info("group_create", logging.Fields{"player": p.Name, "group": id})
	return protocol.OK("group=" + id)
}

// groupInviteLocked handles GROUP INVITE <player>.
func (g *Game) groupInviteLocked(p *Player, target string) string {
	if p.Group == "" {
		return protocol.Err(protocol.ErrNotInGroup, "NOT_IN_GROUP")
	}
	other := g.players[target]
	if other == nil {
		return protocol.Err(protocol.ErrBadRequest, "PLAYER_NOT_FOUND")
	}
	other.Send(protocol.Event("GROUP INVITE", p.Name+" "+p.Group))
	g.log.Info("group_invite", logging.Fields{"player": p.Name, "target": target, "group": p.Group})
	return protocol.OK("")
}

// groupJoinLocked handles GROUP JOIN <group>.
func (g *Game) groupJoinLocked(p *Player, gid string) string {
	if p.Group != "" {
		return protocol.Err(protocol.ErrAlreadyInGroup, "ALREADY_IN_GROUP")
	}
	grp := g.groups[gid]
	if grp == nil {
		return protocol.Err(protocol.ErrBadRequest, "GROUP_NOT_FOUND")
	}
	grp.members[p.Name] = true
	p.Group = gid
	g.broadcastGroup(gid, p.Name, protocol.Event("GROUP JOIN", p.Name))
	g.log.Info("group_join", logging.Fields{"player": p.Name, "group": gid})
	return protocol.OK("group=" + gid)
}

// groupLeaveLocked handles GROUP LEAVE.
func (g *Game) groupLeaveLocked(p *Player) string {
	if p.Group == "" {
		return protocol.Err(protocol.ErrNotInGroup, "NOT_IN_GROUP")
	}
	g.leaveGroupLocked(p)
	return protocol.OK("")
}

// leaveGroupLocked removes p from its group, notifying remaining members and
// cleaning up empty groups. Safe to call when p has no group.
func (g *Game) leaveGroupLocked(p *Player) {
	if p.Group == "" {
		return
	}
	gid := p.Group
	grp := g.groups[gid]
	p.Group = ""
	if grp == nil {
		return
	}
	delete(grp.members, p.Name)
	g.broadcastGroup(gid, p.Name, protocol.Event("GROUP LEAVE", p.Name))
	if len(grp.members) == 0 {
		delete(g.groups, gid)
	}
	g.log.Info("group_leave", logging.Fields{"player": p.Name, "group": gid})
}
